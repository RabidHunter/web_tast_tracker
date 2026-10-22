const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const backoff = (base, attempt, jitter) =>
    base * Math.pow(2, attempt) + (jitter ? Math.floor(Math.random() * 100) : 0);

export async function fetchWithResilience(url, opts = {}) {
    const { retry = {}, idempotencyKey, requestId, ...init } = opts;
    const { retries = 2, baseDelayMs = 250, timeoutMs = 3000, jitter = true } = retry;

    const headers = new Headers(init.headers || {});
    headers.set("Content-Type", "application/json");
    if (idempotencyKey) headers.set("Idempotency-Key", idempotencyKey);
    headers.set("X-Request-Id", requestId || crypto.randomUUID());

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const res = await fetch(url, { ...init, headers, signal: controller.signal });

        if (res.status === 429 && retries >= 1) {
            const retryAfterHeader = res.headers.get("Retry-After");
            const retryAfterMs = Number(retryAfterHeader || 1) * 1000;
            await sleep(retryAfterMs);
            return fetchWithResilience(url, {
                ...opts,
                retry: { ...retry, retries: retries - 1 },
            });
        }

        if (res.status >= 500 && res.status <= 599 && retries >= 1) {
            const attempt = opts.__a || 0;
            await sleep(backoff(baseDelayMs, attempt, jitter));
            return fetchWithResilience(url, {
                ...opts,
                __a: attempt + 1,
                retry: { ...retry, retries: retries - 1 },
            });
        }

        return res;
    } catch (e) {
        if (retries >= 1) {
            const attempt = opts.__a || 0;
            await sleep(backoff(baseDelayMs, attempt, jitter));
            return fetchWithResilience(url, {
                ...opts,
                __a: attempt + 1,
                retry: { ...retry, retries: retries - 1 },
            });
        }
        throw e;
    } finally {
        clearTimeout(timeoutId);
    }
}
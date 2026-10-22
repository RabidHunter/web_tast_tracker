export async function payloadHash(obj) {
    const data = new TextEncoder().encode(JSON.stringify(obj));
    const digest = await crypto.subtle.digest("SHA-256", data);
    return Array.from(new Uint8Array(digest))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
}

export async function getOrReuseKey(payload) {
    const hash = await payloadHash(payload);
    const existingKey = localStorage.getItem(`idem:${hash}`);
    if (existingKey) return existingKey;

    const freshKey = crypto.randomUUID();
    localStorage.setItem(`idem:${hash}`, freshKey);
    return freshKey;
}
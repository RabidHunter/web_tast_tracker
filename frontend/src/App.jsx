import { useState } from 'react'

function App() {
  const [items, setItems] = useState([])

  const loadItems = async () => {
    try {
      const response = await fetch('http://localhost:8000/items')
      const data = await response.json()
      setItems(data)
    } catch (error) {
      console.error("Помилка завантаження даних:", error)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Task Tracker</h1>
      <button
        onClick={loadItems}
        style={{ padding: '10px 20px', fontSize: '16px', marginBottom: '20px', cursor: 'pointer' }}
      >
        Load items
      </button>

      <ul style={{ listStyleType: 'none', padding: 0 }}>
        {items.map(item => (
          <li key={item.id} style={{
            padding: '15px',
            borderBottom: '1px solid #eee',
            display: 'flex',
            alignItems: 'center',
            textDecoration: item.is_completed ? 'line-through' : 'none',
            color: item.is_completed ? '#888' : '#000'
          }}>
            <input
              type="checkbox"
              checked={item.is_completed}
              readOnly
              style={{ marginRight: '15px', transform: 'scale(1.5)' }}
            />
            {item.name}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App
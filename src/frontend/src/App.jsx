import { useState } from 'react'
import beeImage from './assets/bee.jpg'
import plantImage from './assets/plant.jpg'
import './App.css'

const App = () => {
  const [count, setCount] = useState(0);

  return (
    <>
      <div>
        <img src={beeImage} class="logo" />
        <img src={plantImage} class="logo" />

      </div>
      <h1>Bee and Plant Capstone Project</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          Click if you love bees!
        </button>
        <p>❤️ {count}</p>
      </div>
    </>
  )
}

export default App;

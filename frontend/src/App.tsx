import React from 'react';
import './App.css';
import { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState([])
  useEffect(() => {
    fetch("https://dogapi.dog/api/v2/facts", {
      method: "GET"
    })
      .then((res) => {
        console.log(res)
        console.log(res.url)
        return res.json();
      })
      .then((data) => {
        console.log(data)
        // console.log(["data"][0]["attributes"])
        console.log(data["data"][0]["attributes"]["body"])
        setData(data["data"][0]["attributes"]["body"])
      })
  }, [setData])

  return (
    <div className="App">
      <header className="App-header border-black border-2 p-2 m-2">
        <p>
          { data }
        </p>
      </header>
    </div>
  );
}

export default App;

import './Trends.css';
import React, { useState, useEffect } from "react";
import { Url } from './constants'

export function Trends() {
  const [trends, setTrends] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(Url+"/trends/", {
      method: "GET",
      headers: {},
    })
      .then((response) => response.json())
      .then((data) => {
        setTrends(data);
      })
      .catch((error) => setError(error));
  }, []);


  if (error) {
    console.log("error")
    return <p>Error: {error.message}</p>;
  }
  
  // if (trends) {
  return (

    <div className="Trends">

      {trends ? (
            <ul>
                {
                    trends.map((item, key) => {
                        return <li key={key}>{item.tag} {item.count}</li>
                    })
                }
            </ul>
        ) : (
          <p>Loading data...</p>
        )}
    </div>
  )
}

export default Trends;

import './App.css';
import React, { useState, useEffect } from "react";
import { Url } from './constants'

function Spot({ bg, setBg }) {  
  const [imageHash, setImageHash] = useState(null);
  const [spot, setSpot] = useState(null);
  
  const getTime = () => {
    console.log("useEffect getTime, reload data")
    console.log("fetch spot, reload data")

    fetch(Url+"/spot/", {
      method: "GET",
      headers: {},
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("fetched spot - " + data)      
        setImageHash(Date.now());        
        setSpot(data);
        console.log("setBg(Url + spot  + imageHash")
        console.log(Url,spot,imageHash)
        let bgUrl = Url + data + "?" + imageHash
        console.log(bgUrl)
        setBg(bgUrl)
      })
      .catch((error) => {console.log(error)
        // setImageHash(Date.now());
        // setSpot(Url + "/data/trends/spot.jpg");
      });
  };

  useEffect(() => {
    const interval = setInterval(() => getTime(), 10000*2); // 5 miniutes
    // const interval = setInterval(() => getTime(), 10000*60*5); // 5 miniutes
    getTime()
    return () => clearInterval(interval);
  }, []);


  return (
      <div className="App-logo" >
        <img src={bg} alt="logo" className="SpotSmall" />
      </div>
 
  );
}

export default Spot;

// Filename - pages/about.js
import PhotoSlider from '../PhotoSlider.js';

import React from "react";

const Words = ({ bg, setBg }) => {
    return (
        <div>
            <h1>
                words
            </h1>
            <PhotoSlider bg={bg} setBg={setBg}/> 
        </div>
    );
};

export default Words;

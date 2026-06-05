import React, { useEffect, useState } from 'react';
import Slider from 'react-slick';
import { Url } from './constants'

import axios from 'axios';
import './PhotoSlider.css';
const PhotoSlider = ({ bg, setBg }) => {
    const [images, setImages] = useState([]);
    const [oldSlide, setOldSlide] = useState(0);
    const [activeSlide, setActiveSlide] = useState(0);
    const [activeSlide2, setActiveSlide2] = useState(0);
    const [error, setError] = useState(null);
    // const [bg, setBg] = useState([]);
    //const [setBg] = useState([]);

    useEffect(() => {
        // Замена на ваш URL API
        const fetchData = async () => {
            try {
                const response = await axios.get(Url+'/semantic/');
                //console.log(response.data)
                console.log(response.data.length)
                setImages(response.data);                
                setBGTmp()
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
                setError(error);
            }
        };
        fetchData();
    }, []);

    function setBGTmp() {
        if (images.length>0) {
            // console.log(images, activeSlide)
            let bgUrl = images[activeSlide+1]['filename']
            // console.log(setBg)
            console.log(bgUrl, bg)
            setBg(Url+bgUrl)
            console.log(bgUrl, bg)
        }
    }

    const settings = {
        dots: false,
        infinite: true,        
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        arrows: false,
        swipeToSlide: true,
        centerMode: true,
        draggable: true,
        useCSS: 1,
        initialSlide: 5,
        // rows:3,
        pauseOnHover: false,
        // autoplaySpeed: 7000,
        // speed: 4000,
        fade: true,
        autoplaySpeed: 7000,
        speed: 1000,
        beforeChange: (current, next) => {
            setOldSlide(current);
            setActiveSlide(next);
            setBGTmp()
            // if (activeSlide+1 < images.length) {
            // }
        },
        afterChange: current => setActiveSlide2(current)

    };

    if (error) {
        console.log("error")
        return <p>Error: {error.message}</p>;
    } else return (
        <div className="slider-container">
            <Slider {...settings}>
                
                {images.map((image, index) => (

                    <div key={index} className="item">

                        <h3>
                        {/* {image.x}<strong>{oldSlide}-{activeSlide}</strong>-{index}-{activeSlide} */}
                        </h3>

                        <div className="img-info shake" style={{visibility: (index !== oldSlide)?"visible":"visible"}}>
                            <h4>Семантические координаты:
                            ({image.x}; {image.y}; {image.z})</h4>
                        </div>

                        <h2 className="slider-h2 shake">{image.tag}

                        </h2>

                        <div className="tmb-src shake">
                            <img src={Url + image.filename_src} alt={image.tag} className="img-src"  />
                            <img src={Url+ image.filename_pal} alt={image.tag} className="img-src"  />
                            <img src={Url+ image.filename_som} alt={image.tag} className="img-src"  />                                                    
                        </div>

                        

                        <img src={Url+ image.filename} alt={image.tag} className="imgimg shake"/>
                    </div>
                ))}
            </Slider>
        </div>
    );
};

export default PhotoSlider;

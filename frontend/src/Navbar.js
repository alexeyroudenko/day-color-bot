// Filename - "./components/Navbar.js

import React from "react";
import { Nav, NavLink, NavMenu } from "./Navbar2";

const Navbar = () => {
    return (
        <>
            <Nav>
                <NavMenu>
                    <NavLink to="/">
                    spot
                    </NavLink>
                    <NavLink to="/words">
                    words
                    </NavLink>
                    <NavLink to="/contact">
                    contact
                    </NavLink>
                </NavMenu>
            </Nav>
        </>
    );
};

export default Navbar;

var found_locations = {};
            
function change_location(link_url) {
    $('#location_search').modal('show');
}

function show_error( msg ) {
    container = document.getElementById("error_msg");
    if (container) {
        if (container.msg && container.msg === msg) return;
        container.msg = msg;

        div_elem = document.createElement("div");
        div_elem.className = "alert alert-warning alert-dismissible fade show";
        div_elem.setAttribute("role", "alert");
        div_elem.innerHTML = msg
        

        btn_elem = document.createElement("button");
        btn_elem.setAttribute("type", "button");
        btn_elem.setAttribute("class", "close");
        btn_elem.setAttribute("data-dismiss", "alert");
        btn_elem.setAttribute("aria-label", "Close");
        btn_elem.innerHTML = "<span aria-hidden='true'>&times;</span>";

        div_elem.appendChild(btn_elem);
        container.appendChild(div_elem);

        setTimeout(
            function() {container.innerHTML = '';container.msg = ''},
            6000
        );
    }
}

function get_search_values() {
    address = document.getElementById("address-input")?.value;
    address = address ? address.trim() : null;

    place = document.getElementById("place-input")?.value
    place = place ? place.trim() : null;

    country = document.getElementById("country-input")?.value
    country = country ? country.trim() : null;
    
    if (address) {
        place_type = 'address';
    } else if (place) {
        place_type = "place";
    } else if (country) {
        place_type = "country";
    } else {
        return null;
    } 

    switch (place_type) {
        case 'address':
            place_name = address;
            if (place) {
                place_name += (", " + place);
            }
            if (country) {
                place_name += (", " + country);
            }
            break;
        case 'place':
            place_name = place;
            if (country) {
                place_name += (", " + country);
            }
            break;
        case 'country':
            place_name = country;
            break;
        default:
            return null;
    }
    return {'place_type': place_type, 'place_name': place_name}
}

async function find_location(find_url) {
    try {   
        let search_params = get_search_values();
        let accept_btn = document.getElementById("accept_btn")

        let locations_container = document.getElementById('locations_select')
        if (!locations_container || !accept_btn) {
            throw Error("Locations could not be processed. Refresh the webpage and try again.")
        }
        locations_container.innerHTML = "";

        if (search_params) {
            if (!find_url) {
                throw Error("Request could not be sent. Refresh the webpage and try again.")
            }

            find_location_url = find_url + '?place_name=' + encodeURIComponent(search_params.place_name);
            find_location_url += "&place_type=" + encodeURIComponent(search_params.place_type);

            let response = await fetch(find_location_url);

            if (response.status === 200) {
                let json = await response.json()

                found_locations = (json) ? json.locations : [];
                
                if (!found_locations || !found_locations.length) throw Error("The search returned no locations. Refine your request and try again.");

                let heading_elem = document.createElement("h6");
                heading_elem.innerText = "Select one of the following matches:"
                locations_container.appendChild(heading_elem);

                found_locations.forEach( function(location, index) {
                    if (location.place_name && location.place_type && location.latitude && location.longitude) { 

                        let radio = document.createElement("input");
                        radio.setAttribute('name', 'location_choice');
                        radio.setAttribute('type', 'radio');
                        radio.setAttribute('id', 'location' + index);
                        radio.setAttribute('value', index);
                        radio.checked = !index;
                        locations_container.appendChild(radio);

                        let radio_label = document.createElement("label");
                        radio_label.setAttribute('for', 'location' + index);
                        radio_label.className = "pl-1";
                        radio_label.innerText = location.place_name;
                        locations_container.appendChild(radio_label);

                        let br_elem = document.createElement("br");
                        locations_container.appendChild(br_elem);
                    } else {
                        locations_container.innerHTML = "";
                        throw Error("The search returned incomplete values. Refine your request and try again.")
                    }
                });
                accept_btn.disabled = false;
                
            } else {
                throw Error(response.statusText);
            }
        } else {
            throw Error("Provide values for address, city/town and/or country, then try again.")
        }
    }
    catch (error) {
            show_error("<strong>Your search returned an error:</strong><br>" + error.message);
            if (accept_btn) accept_btn.disabled = true;
    } 
}

function display_location(index) {
    let location = found_locations[index];
    if (!location) throw Error("Location could not be retrieved.")

    let place_type_elem = document.getElementById("place_type");
    let place_name_elem = document.getElementById("place_name");
    let latitude_elem = document.getElementById("latitude");
    let longitude_elem = document.getElementById("longitude");
    if (place_name_elem && place_type_elem && latitude_elem && longitude_elem) {
        if (location.place_type === "place") {
            place_type_elem.innerText = "City/Town";
        } else {
            const place_string = location.place_type;
            place_type_elem.innerText = place_string.charAt(0).toUpperCase() + place_string.slice(1);
        }
        place_name_elem.innerText = location.place_name;
        latitude_elem.innerText = location.latitude;
        longitude_elem.innerText = location.longitude;
    } else {
        throw Error("Location could not be updated.");
    }
}

function accept_location() {
    try {   
        if (!found_locations) throw Error("Locations are invalid. Reopen this dialog and try again.");

        let radio_elems = document.getElementsByName("location_choice");
        if (!radio_elems) throw Error("Location options are invalid. Reopen this dialog and try again.");
        for (i = 0; i<radio_elems.length; i++) {
            if (radio_elems[i].checked) {
                display_location(radio_elems[i].value);
                $('#location_search').modal('hide');
                return
            }
        }
        throw Error("Location to accept not found.")
    }
    catch (error) {
        show_error("<strong>Location not accepted:</strong><br>" + error.message);
    } 
}

import { useEffect, useRef, useState } from "react";
import { Box, Flex, Input, InputGroup, Button } from "@chakra-ui/react";
import { LuLocateFixed } from "react-icons/lu";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const InteractiveMap = ({ 
  selectedCoords, 
  setSelectedCoords,
  setErrorDialogMsg
}) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null); 

  // helper function to place marker on click or type
  const placeMarker = (lng, lat) => {
    if (!mapRef.current) return;

    const isValid =
      typeof lat === "number" &&
      typeof lng === "number" &&
      lat >= -90 && lat <= 90 &&
      lng >= -180 && lng <= 180;

    if (!isValid) {
      setErrorDialogMsg(`Invalid coordinates: latitude must be between -90 and 90, 
        longitude between -180 and 180.`);
      return;
    }

    try {
      if (!markerRef.current) {
        markerRef.current = new maplibregl.Marker();
      }
      markerRef.current.setLngLat([lng, lat]).addTo(mapRef.current);
    } catch (err) {
      setErrorDialogMsg(err.message);
    }
  };

  // initialize map + handle click to place marker
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: "./custom-map-style.json",
      center: [-120, 44],
      zoom: 6,
    });

    mapRef.current = map;

    map.on("click", (event) => {
      const { lng, lat } = event.lngLat;
      // note: we are choosing to reverse the order here (aligns with backend/other convention)
      setSelectedCoords({ lat, lng });

      placeMarker(lng, lat);
    });

    return () => map.remove();
  }, []);

  // side effect to handle user typing in coordinates
  useEffect(() => {
    const { lat, lng } = selectedCoords;
  
    if (!lat || !lng) return;
    const latNum = Number(lat);
    const lngNum = Number(lng);
    if (isNaN(latNum) || isNaN(lngNum)) return;
  
    placeMarker(lngNum, latNum);
  }, [selectedCoords]);

  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      <Flex gap={2} direction={{ base: "column", md: "row" }}>
        {/* Lat/Long input fields */}
        <InputGroup startAddon="Latitude" flex={{ base: "1", md: "auto" }}>
          <Input
            placeholder="Type or click on the map!"
            type="number"
            value={selectedCoords.lat}
            onChange={(e) =>
              setSelectedCoords((prev) => ({ ...prev, lat: e.target.value }))
            }
          />
        </InputGroup>
        <InputGroup startAddon="Longitude" flex={{ base: "1", md: "auto" }}>
          <Input
            placeholder="Type or click on the map!"
            type="number"
            value={selectedCoords.lng}
            onChange={(e) =>
              setSelectedCoords((prev) => ({ ...prev, lng: e.target.value }))
            }
          />
        </InputGroup>
      </Flex>

      {/* MAP BOX (replaces your placeholder) */}
      <Box
        flex="1"
        borderWidth="2px"
        borderRadius="md"
        bg="gray.100"
        overflow="hidden"
      >
        {/* This is the actual map container */}
        <Box
          ref={mapContainerRef}
          id="map"
          style={{ width: "100%", height: "100%" }}
        />
      </Box>
    </Flex>
  );
};

export default InteractiveMap;

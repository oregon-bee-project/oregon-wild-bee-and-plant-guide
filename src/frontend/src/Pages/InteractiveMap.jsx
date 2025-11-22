import { useEffect, useRef, useState } from "react";
import { Box, Flex, Input, InputGroup, Button } from "@chakra-ui/react";
import { LuLocateFixed } from "react-icons/lu";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const InteractiveMap = ({ 
  selectedCoords, 
  setSelectedCoords, 
  fetchLocationData 
}) => {
  const mapContainerRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: "./custom-map-style.json",
      center: [-120, 44],
      zoom: 6,
    });

    // WILL NEED TO REDO THIS PART
    let marker = null;

    map.on("click", (event) => {
      const { lng, lat } = event.lngLat;
      // note: we are choosing to reverse the order here (aligns with backend/other convention)
      setSelectedCoords({ lat, lng });

      // Remove previous marker
      if (marker) marker.remove();

      // Add new marker
      marker = new maplibregl.Marker().setLngLat([lng, lat]).addTo(map);
    });

    return () => map.remove();
  }, []);

  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      <Flex gap={2}>

        {/* Lat/Long input fields */}
        <InputGroup startAddon="Latitude">
          <Input
            placeholder="Type or click on the map!"
            value={selectedCoords.lat}
            onChange={(e) =>
              setSelectedCoords((prev) => ({ ...prev, lat: e.target.value }))
            }
          />
        </InputGroup>
        <InputGroup startAddon="Longitude">
          <Input
            placeholder="Type or click on the map!"
            value={selectedCoords.lng}
            onChange={(e) =>
              setSelectedCoords((prev) => ({ ...prev, lng: e.target.value }))
            }
          />
        </InputGroup>

        <Button
          bg="red.600"
          _hover={{bg: "red.500"}}
          onClick={fetchLocationData}
        >
          <LuLocateFixed /> Set Location
        </Button>
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

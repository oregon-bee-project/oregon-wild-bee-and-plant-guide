import { useEffect, useRef, useState } from "react";
import { Box, Flex, Text, Button } from "@chakra-ui/react";
import { LuMapPin } from "react-icons/lu";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const InteractiveMap = () => {
  const mapContainerRef = useRef(null);
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: import.meta.env.BASE_URL + "custom-map-style.json",
      center: [-120, 44],
      zoom: 6,
    });

    // WILL NEED TO REDO THIS PART
    let marker = null;

    map.on("click", (event) => {
      const { lng, lat } = event.lngLat;
      setSelectedLocation({ lng, lat });

      // Remove previous marker
      if (marker) marker.remove();

      // Add new marker
      marker = new maplibregl.Marker().setLngLat([lng, lat]).addTo(map);
    });

    return () => map.remove();
  }, []);

  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>

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

      {/* button */}
      <Button bg="green.400">
        <LuMapPin /> Set Location
      </Button>

      {/* Coordinates display WILL NOT WANT TO ACTUALLY DO THIS FOR THE FINAL PRODUCT 
      {selectedLocation && (
        <Text fontSize="sm" mt={2}>
          Selected Coordinates:<br />
          Lat: {selectedLocation.lat.toFixed(5)}, Lng:{" "}
          {selectedLocation.lng.toFixed(5)}
        </Text>
      )} */}
    </Flex>
  );
};

export default InteractiveMap;

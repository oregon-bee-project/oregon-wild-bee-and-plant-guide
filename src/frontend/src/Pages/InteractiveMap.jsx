import { useEffect, useRef, useState } from "react";
import {
  Box,
  Flex,
  Input,
  Group,
  InputAddon,
  Button,
  Portal,
  Select,
  Text,
  createListCollection,
} from "@chakra-ui/react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const overlays = createListCollection({
  items: [
    { label: "County", value: "county", color: "Orange" },
    { label: "Ecoregion", value: "ecoregion", color: "Green" },
    { label: "National Forest", value: "national-forest", color: "Brown" },
  ],
});

const InteractiveMap = ({
  selectedCoords,
  setSelectedCoords,
  setErrorDialogMsg,
  setSelectedRegion,
}) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const selectedFeatureRef = useRef(null);
  const [address, setAddress] = useState("");

  const handleLayerChange = (e) => {
    const selectedCategory = e.value[0];
    setSelectedRegion(selectedCategory);
    if (!mapRef.current) return;

    overlays.items.forEach((item) => {
      const layerId = `${item.value}-layer`;
      const outlineId = `${layerId}-outline`;
      const visibility = item.value === selectedCategory ? "visible" : "none";

      if (mapRef.current.getLayer(layerId)) {
        mapRef.current.setLayoutProperty(layerId, "visibility", visibility);
        mapRef.current.setLayoutProperty(outlineId, "visibility", visibility);
      }
    });
  };

  const placeMarker = (lng, lat) => {
    if (!mapRef.current) return;
    if (!markerRef.current) {
      markerRef.current = new maplibregl.Marker();
    }
    markerRef.current.setLngLat([lng, lat]).addTo(mapRef.current);
  };

  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: "./custom-map-style.json",
      center: [-120.55, 43.8],
      zoom: 6,
    });

    mapRef.current = map;
    let hoveredFeature = null;

    map.on("load", () => {
      // Set default region to match UI default
      setSelectedRegion("county");

      overlays.items.forEach((item) => {
        const sourceId = `${item.value}-source`;
        const layerId = `${item.value}-layer`;

        // 1. Add Source
        map.addSource(sourceId, {
          type: "geojson",
          data: `/bee-plant-data-exploration/GeoJSON/${item.value}.json`,
          generateId: true,
        });

        // 2. Add Fill Layer
        map.addLayer({
          id: layerId,
          type: "fill",
          source: sourceId,
          layout: { visibility: item.value === "county" ? "visible" : "none" },
          paint: {
            "fill-color": item.color,
            "fill-opacity": [
              "case",
              ["boolean", ["feature-state", "selected"], false],
              0.8,
              ["boolean", ["feature-state", "hover"], false],
              0.6,
              0,
            ],
          },
        });

        // 3. Add Border Layer
        map.addLayer({
          id: `${layerId}-outline`,
          type: "line",
          source: sourceId,
          layout: { visibility: item.value === "county" ? "visible" : "none" },
          paint: {
            "line-color": "#000000",
            "line-opacity": 0.2,
            "line-width": 0.5,
          },
        });

        // Hover Logic
        map.on("mousemove", layerId, (e) => {
          if (e.features.length > 0) {
            if (hoveredFeature) {
              map.setFeatureState(
                { source: hoveredFeature.source, id: hoveredFeature.id },
                { hover: false },
              );
            }
            hoveredFeature = { id: e.features[0].id, source: sourceId };
            map.setFeatureState(
              { source: sourceId, id: hoveredFeature.id },
              { hover: true },
            );
            map.getCanvas().style.cursor = "pointer";
          }
        });

        map.on("mouseleave", layerId, () => {
          if (hoveredFeature && hoveredFeature.source === sourceId) {
            map.setFeatureState(
              { source: hoveredFeature.source, id: hoveredFeature.id },
              { hover: false },
            );
            hoveredFeature = null;
          }
          map.getCanvas().style.cursor = "";
        });

        map.on("click", layerId, (e) => {
          if (!e.features.length) return;
          const feature = e.features[0];
          // Clear previous selection
          if (selectedFeatureRef.current) {
            map.setFeatureState(selectedFeatureRef.current, {
              selected: false,
            });
          }
          // Set new selection
          selectedFeatureRef.current = {
            source: sourceId,
            id: feature.id,
          };
          map.setFeatureState(selectedFeatureRef.current, { selected: true });
          // Update coords + marker
          const { lng, lat } = e.lngLat;
          setSelectedCoords({ lat, lng });
          placeMarker(lng, lat);
        });
      });
    });

    return () => map.remove();
  }, []);

  const geocodeAddress = async (address) => {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`
    );

    const data = await response.json();

    if (data.length > 0) {
      return {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon),
      };
    } else {
      throw new Error("No results found");
    }
  };

  const handleSetAddress = async () => {
    if (!address) return;

    try {
      const coords = await geocodeAddress(address);

      setSelectedCoords(coords);

      // Center map + place marker
      if (mapRef.current) {
        mapRef.current.flyTo({
          center: [coords.lng, coords.lat],
          zoom: 14,
        });
      }

      placeMarker(coords.lng, coords.lat);
    } catch (err) {
      setErrorDialogMsg("Address not found.");
    }
  };


  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      <Flex gap={2} direction={{ base: "column", md: "row" }} align="center">
        <Text>I want to learn about bees and plants in the</Text>
        {/* <Group attached flex={{ base: "1", md: "2" }}>
          <InputAddon>Latitude</InputAddon>
          <Input
            type="number"
            value={selectedCoords.lat}
            onChange={(e) =>
              setSelectedCoords((prev) => ({ ...prev, lat: e.target.value }))
            }
          />
        </Group>
        <Group attached flex={{ base: "1", md: "2" }}>
          <InputAddon>Longitude</InputAddon>
          <Input
            type="number"
            value={selectedCoords.lng}
            onChange={(e) =>
              setSelectedCoords((prev) => ({ ...prev, lng: e.target.value }))
            }
          />
        </Group> */}

        <Select.Root
          minW={{base: "100%", md: "10%"}}
          maxW={{base: "100%", md: "15%"}}
          collection={overlays}
          flex={{ base: "1", md: "1" }}
          defaultValue={["county"]}
          onValueChange={handleLayerChange}
        >
          <Select.HiddenSelect />
          <Select.Control>
            <Select.Trigger>
              <Select.ValueText placeholder="Select overlay" />
            </Select.Trigger>
            <Select.IndicatorGroup>
              <Select.Indicator />
            </Select.IndicatorGroup>
          </Select.Control>
          <Portal>
            <Select.Positioner>
              <Select.Content>
                {overlays.items.map((overlays) => (
                  <Select.Item item={overlays} key={overlays.value}>
                    {overlays.label}
                    <Select.ItemIndicator />
                  </Select.Item>
                ))}
              </Select.Content>
            </Select.Positioner>
          </Portal>
        </Select.Root>
        <Text>near this location:</Text>
        <Group
          attached
          w="full"
          minW={{base: "100%", md: "60%"}}
          maxW={{base: "100%", md: "60%"}}
        >
          <Input
            flex="1"
            placeholder="Type an address, or click on the map"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
          />
          <Button
            variant="outline"
            bg="bg.subtle"
            _hover={{ bg: "green.100" }}
            onClick={handleSetAddress}
          >
            Set Address
          </Button>
        </Group>
      </Flex>

      <Box
        flex="1"
        borderWidth="2px"
        borderRadius="md"
        bg="gray.100"
        overflow="hidden"
      >
        <Box ref={mapContainerRef} style={{ width: "100%", height: "100%" }} />
      </Box>
    </Flex>
  );
};

export default InteractiveMap;

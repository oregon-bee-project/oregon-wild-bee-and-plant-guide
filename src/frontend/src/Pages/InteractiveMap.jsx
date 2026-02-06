import { useEffect, useRef, useState } from "react";
import { Box, Flex, Input, Group, InputAddon, Button, Portal, Select, createListCollection } from "@chakra-ui/react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const overlays = createListCollection({
  items: [
    { label: "County", value: "county", color: "Orange" },
    { label: "Ecoregion", value: "ecoregion", color: "Green" },
    { label: "National Forest", value: "national-forest", color: "Brown" },
  ],
})

const InteractiveMap = ({
  selectedCoords,
  setSelectedCoords,
  setErrorDialogMsg,
  setSelectedRegion
}) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);

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
      center: [-120.55, 43.80],
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
                { hover: false }
              );
            }
            hoveredFeature = { id: e.features[0].id, source: sourceId };
            map.setFeatureState(
              { source: sourceId, id: hoveredFeature.id },
              { hover: true }
            );
            map.getCanvas().style.cursor = "pointer";
          }
        });

        map.on("mouseleave", layerId, () => {
          if (hoveredFeature && hoveredFeature.source === sourceId) {
            map.setFeatureState(
              { source: hoveredFeature.source, id: hoveredFeature.id },
              { hover: false }
            );
            hoveredFeature = null;
          }
          map.getCanvas().style.cursor = "";
        });
      });
    });

    map.on("click", (event) => {
      const { lng, lat } = event.lngLat;
      setSelectedCoords({ lat, lng });
      placeMarker(lng, lat);
    });

    return () => map.remove();
  }, []);

  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      <Flex gap={2} direction={{ base: "column", md: "row" }}>
        <Group attached flex={{ base: "1", md: "2" }}>
          <InputAddon>Latitude</InputAddon>
          <Input
            type="number"
            value={selectedCoords.lat}
            onChange={(e) => setSelectedCoords(prev => ({ ...prev, lat: e.target.value }))}
          />
        </Group>
        <Group attached flex={{ base: "1", md: "2" }}>
          <InputAddon>Longitude</InputAddon>
          <Input
            type="number"
            value={selectedCoords.lng}
            onChange={(e) => setSelectedCoords(prev => ({ ...prev, lng: e.target.value }))}
          />
        </Group>

        <Select.Root
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

      </Flex>

      <Box flex="1" borderWidth="2px" borderRadius="md" bg="gray.100" overflow="hidden">
        <Box ref={mapContainerRef} style={{ width: "100%", height: "100%" }} />
      </Box>
    </Flex>
  );
};

export default InteractiveMap;
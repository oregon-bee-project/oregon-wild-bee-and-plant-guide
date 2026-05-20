import { useEffect, useRef, useState } from "react";
import {
  Box,
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
  selectedRegion,
  setSelectedRegion,
  mapResetTrigger,
}) => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const selectedFeatureRef = useRef(null);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

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

  const clearSelectedFeature = () => {
    if (!mapRef.current || !selectedFeatureRef.current) return;
    mapRef.current.setFeatureState(selectedFeatureRef.current, { selected: false });
    selectedFeatureRef.current = null;
  };

  const highlightRegionAtCoords = (lng, lat, region) => {
    if (!mapRef.current || !region) return false;

    const sourceId = `${region}-source`;
    const layerId = `${region}-layer`;
    if (!mapRef.current.getLayer(layerId)) return false;

    const point = mapRef.current.project([lng, lat]);
    const features = mapRef.current.queryRenderedFeatures(point, { layers: [layerId] });
    if (!features.length) return false;

    const featureId = features[0].id;
    if (featureId === undefined || featureId === null) return false;

    clearSelectedFeature();
    selectedFeatureRef.current = { source: sourceId, id: featureId };
    mapRef.current.setFeatureState(selectedFeatureRef.current, { selected: true });
    return true;
  };

  useEffect(() => {
    clearSelectedFeature();
  }, [mapResetTrigger]);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: `${import.meta.env.BASE_URL}custom-map-style.json`,
      center: [-120.55, 43.8],
      zoom: 6,
    });

    mapRef.current = map;
    let hoveredFeature = null;

    map.on("load", () => {
      const initialRegion = selectedRegion || "county";
      if (!selectedRegion) {
        setSelectedRegion("county");
      }

      overlays.items.forEach((item) => {
        const sourceId = `${item.value}-source`;
        const layerId = `${item.value}-layer`;

        // 1. Add Source
        map.addSource(sourceId, {
          type: "geojson",
          data: `${import.meta.env.BASE_URL}GeoJSON/${item.value}.json`,
          generateId: true,
        });

        // 2. Add Fill Layer
        map.addLayer({
          id: layerId,
          type: "fill",
          source: sourceId,
          layout: { visibility: item.value === initialRegion ? "visible" : "none" },
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
          layout: { visibility: item.value === initialRegion ? "visible" : "none" },
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
          clearSelectedFeature();
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
      setIsMapLoaded(true);
    });

    return () => map.remove();
  }, []);

  useEffect(() => {
    if (!mapRef.current || !isMapLoaded || !selectedRegion) return;

    overlays.items.forEach((item) => {
      const layerId = `${item.value}-layer`;
      const outlineId = `${layerId}-outline`;
      const visibility = item.value === selectedRegion ? "visible" : "none";

      if (mapRef.current.getLayer(layerId)) {
        mapRef.current.setLayoutProperty(layerId, "visibility", visibility);
      }
      if (mapRef.current.getLayer(outlineId)) {
        mapRef.current.setLayoutProperty(outlineId, "visibility", visibility);
      }
    });
  }, [isMapLoaded, selectedRegion]);

  useEffect(() => {
    if (!mapRef.current || !isMapLoaded) return;
    if (selectedCoords.lat === "" || selectedCoords.lng === "") return;

    let timeoutId;
    placeMarker(selectedCoords.lng, selectedCoords.lat);

    const region = selectedRegion || "county";
    const wasHighlighted = highlightRegionAtCoords(selectedCoords.lng, selectedCoords.lat, region);

    // On remount, rendered features can lag behind map load; retry once after render settles.
    if (!wasHighlighted) {
      mapRef.current.once("idle", () => {
        const highlightedOnIdle = highlightRegionAtCoords(selectedCoords.lng, selectedCoords.lat, region);
        if (!highlightedOnIdle) {
          timeoutId = window.setTimeout(() => {
            highlightRegionAtCoords(selectedCoords.lng, selectedCoords.lat, region);
          }, 150);
        }
      });
    }

    return () => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [isMapLoaded, selectedCoords, selectedRegion]);


  return (
    <Box
      flex="1"
      borderWidth="2px"
      borderRadius="md"
      bg="gray.100"
      overflow="hidden"
    >
      <Box ref={mapContainerRef} style={{ width: "100%", height: "100%" }} />
    </Box>
  );
};

export default InteractiveMap;

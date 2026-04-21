import { useRef, useState } from "react";
import { Flex, Button, useDisclosure, Drawer, Text } from "@chakra-ui/react";
import { LuMenu, LuCheck } from "react-icons/lu";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "./InteractiveMap";
import DataDisplay from "./DataDisplay";
import ErrorDialog from "../CustomComponents/ErrorDialog";
import LoadingDialog from "../CustomComponents/LoadingDialog";

// This is the main webpage content - everything below the header

const MainContent = () => {
  const [activePage, setActivePage] = useState("prompts-map");
  const [selectedCoords, setSelectedCoords] = useState({ lat: "", lng: "" });
  const [selectedRegion, setSelectedRegion] = useState("");
  const [locationData, setLocationData] = useState(null);
  const [activePrompt, setActivePrompt] = useState(null);
  const [errorDialogMsg, setErrorDialogMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const activeRequestControllerRef = useRef(null);
  const { open, onOpen, onClose } = useDisclosure();

  const API_BASE = import.meta.env.PROD
    ? "https://bee-data-api.onrender.com" // this is what the url prefix will be in production
    : ""; // this is what the url prefix will be in dev

  const fetchLocationData = async () => {
    if (isLoading) {
      return;
    }

    if (!activePrompt) {
      setErrorDialogMsg("Please choose a prompt.");
      return;
    }

    // check that coordinate fields are populated
    if (selectedCoords.lat == "" || selectedCoords.lng == "") {
      setErrorDialogMsg("Please set a value for both Latitude and Longitude.");
      return;
    }

    if (activePrompt === 1 && selectedRegion == "") {
      setErrorDialogMsg("Please set a value for region.");
      return;
    }

    // set loading state to true before making API call
    setIsLoading(true);
    activeRequestControllerRef.current?.abort();
    const controller = new AbortController();
    activeRequestControllerRef.current = controller;

    const parseApiErrorMessage = async (res, fallback) => {
      try {
        const errorJson = await res.json();
        if (typeof errorJson?.detail === "string") return errorJson.detail;
        if (errorJson?.detail?.message) {
          const retry = errorJson.detail.retryAfterSeconds;
          return Number.isFinite(retry)
            ? `${errorJson.detail.message} Try again in ${retry} seconds.`
            : errorJson.detail.message;
        }
      } catch {
        // ignore parse failure
      }
      return fallback;
    };

    try {
      if (activePrompt === 1) {
        const params = new URLSearchParams({
          lat: selectedCoords.lat,
          long: selectedCoords.lng,
          region_type: selectedRegion.toLowerCase(),
        });
        const res = await fetch(`${API_BASE}/api/location-data/?${params.toString()}`, {
          signal: controller.signal,
        });
        if (!res.ok) {
          const msg = await parseApiErrorMessage(res, "Request failed");
          throw new Error(msg);
        }
        const json = await res.json();
        setLocationData(json);
        setActivePage("data-display");
      } else if (activePrompt === 2) {
        const params = new URLSearchParams({
          lat: selectedCoords.lat,
          long: selectedCoords.lng,
          region_type: (selectedRegion || "county").toLowerCase(),
        });
        const res = await fetch(`${API_BASE}/api/best-plants-to-plant/?${params.toString()}`, {
          signal: controller.signal,
        });
        if (!res.ok) {
          const msg = await parseApiErrorMessage(res, "Request failed");
          throw new Error(msg);
        }
        const json = await res.json();
        if (json.error) {
          throw new Error(json.err_msg || "Error fetching best plants");
        }
        setLocationData(json);
        setActivePage("data-display");
      } else if (activePrompt === 3) {
        const params = new URLSearchParams({
          lat: selectedCoords.lat,
          long: selectedCoords.lng,
          region_type: selectedRegion.toLowerCase(),
          species_offset: "0",
          species_limit: "25",
        });
        const res = await fetch(`${API_BASE}/api/detailed-report/?${params.toString()}`, {
          signal: controller.signal,
        });
        if (!res.ok) {
          const msg = await parseApiErrorMessage(res, "Request failed");
          throw new Error(msg);
        }
        const json = await res.json();
        setLocationData(json);
        setActivePage("data-display");
      }
    } catch (err) {
      if (err?.name === "AbortError") {
        return;
      }
      console.error("Error fetching location data:", err.message, err);
      if (err.message == "Region not found using provided Shape Files") {
        setErrorDialogMsg(`Unable to fetch data for the selected
                    coordinates. Please pick a different location on the map.`);
      } else {
        setErrorDialogMsg(err.message || "An error occurred while fetching data. Please try again.");
      }
    } finally {
      setIsLoading(false);
      if (activeRequestControllerRef.current === controller) {
        activeRequestControllerRef.current = null;
      }
    }
  };

  // Determine which page to render
  const isPromptsMapPage = activePage == "prompts-map";

  return (
    <>
      {errorDialogMsg && (
        <ErrorDialog
          message={errorDialogMsg}
          onClose={() => setErrorDialogMsg("")}
        />
      )}

      <LoadingDialog isOpen={isLoading} />

      <Flex
        h="100%"
        p={{ base: "5px", md: "10px" }}
        gap={{ base: "10px", md: "30px" }}
        direction={{ base: "column", md: "row" }}
      >
        {isPromptsMapPage ? (
          <>
            {/* Mobile hamburger menu button - only visible on mobile */}
            <Button
              variant="outline"
              borderColor="black"
              display={{ base: "flex", md: "none" }}
              onClick={onOpen}
              width="100%"
            >
              {activePrompt ? (
                <Flex align="center" gap={2}>
                  <LuCheck />
                  <Text>Prompt Selected</Text>
                </Flex>
              ) : (
                <Flex align="center" gap={2}>
                  <LuMenu />
                  <Text>Show Prompts</Text>
                </Flex>
              )}
            </Button>

            {/* Desktop sidebar - hidden on mobile */}
            <PromptSidebar
              display={{ base: "none", md: "flex" }} // hidden on mobile
              activePrompt={activePrompt}
              setActivePrompt={setActivePrompt}
              fetchLocationData={fetchLocationData}
              showButton={true}
              setErrorDialogMsg={setErrorDialogMsg}
            />

            {/* Mobile drawer for sidebar */}
            <Drawer.Root
              open={open}
              onOpenChange={(e) => {
                if (!e.open) onClose();
              }}
              placement="top"
            >
              <Drawer.Backdrop />
              <Drawer.Content rounded="md">
                <Drawer.Body>
                  <PromptSidebar
                    activePrompt={activePrompt}
                    setActivePrompt={setActivePrompt}
                    fetchLocationData={fetchLocationData}
                    onPromptSelect={onClose}
                    showButton={false}
                  />
                  <Button mt="2" w="100%" onClick={onClose}>
                    Done
                  </Button>
                </Drawer.Body>
              </Drawer.Content>
            </Drawer.Root>

            <InteractiveMap
              selectedCoords={selectedCoords}
              setSelectedCoords={setSelectedCoords}
              setErrorDialogMsg={setErrorDialogMsg}
              selectedRegion={selectedRegion}
              setSelectedRegion={setSelectedRegion}
            />
          </>
        ) : (
          <DataDisplay
            locationData={locationData}
            activePrompt={activePrompt}
            selectedCoords={selectedCoords}
            setActivePage={setActivePage}
            setActivePrompt={setActivePrompt}
            setSelectedCoords={setSelectedCoords}
            selectedRegion={selectedRegion}
          />
        )}
      </Flex>
    </>
  );
};

export default MainContent;

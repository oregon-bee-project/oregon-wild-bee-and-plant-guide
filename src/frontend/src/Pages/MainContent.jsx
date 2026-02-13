import { useState } from "react";
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
  const { open, onOpen, onClose } = useDisclosure();

  const API_BASE = import.meta.env.PROD
    ? "https://bee-data-api.onrender.com" // this is what the url prefix will be in production
    : ""; // this is what the url prefix will be in dev

  const fetchLocationData = async () => {
    if (!activePrompt) {
      setErrorDialogMsg("Please choose a prompt.");
      return;
    }

    // check that coordinate fields are populated
    if (selectedCoords.lat == "" || selectedCoords.lng == "") {
      setErrorDialogMsg("Please set a value for both Latitude and Longitude.");
      return;
    }

    if (selectedRegion == "") {
      setErrorDialogMsg("Please set a value for region.");
      return;
    }

    // set loading state to true before making API call
    setIsLoading(true);

    const params = new URLSearchParams({
      lat: selectedCoords.lat,
      long: selectedCoords.lng,
      region_type: selectedRegion.toLowerCase(),
    });

    try {
      const res = await fetch(
        `${API_BASE}/api/location-data/?${params.toString()}`,
      );

      if (!res.ok) {
        const errorJson = await res.json();
        throw new Error(errorJson.detail);
      }

      const json = await res.json();
      setLocationData(json);
      setActivePage("data-display");
    } catch (err) {
      console.error(err.message);
      if (err.message == "Region not found using provided Shape Files") {
        setErrorDialogMsg(`Unable to fetch data for the selected
                    coordinates. Please pick a different location on the map.`);
      }
    } finally {
      setIsLoading(false);
    }
  };

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
        {activePage == "prompts-map" ? (
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
              setSelectedRegion={setSelectedRegion}
            />
          </>
        ) : (
          <DataDisplay
            locationData={locationData}
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

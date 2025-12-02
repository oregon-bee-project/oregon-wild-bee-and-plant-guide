import { useState } from "react";
import { Flex, Tabs } from "@chakra-ui/react";
import { LuChartColumn, LuMap } from "react-icons/lu";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "./InteractiveMap";
import DataDisplay from "./DataDisplay";
import ErrorDialog from "../CustomComponents/ErrorDialog";

// This is the main webpage content - everything below the header

const MainContent = () => {
    const [currentTab, setCurrentTab] = useState("map");
    const [selectedCoords, setSelectedCoords] = useState({ lat: "", lng: "" });
	const [locationData, setLocationData] = useState(null);
    const [activePrompt, setActivePrompt] = useState(null);
    const [errorDialogMsg, setErrorDialogMsg] = useState("");

	const API_BASE = import.meta.env.PROD
		? "https://bee-data-api.onrender.com"		// this is what the url prefix will be in production
		: "";																		// this is what the url prefix will be in dev

	const fetchLocationData = async () => {

        if (!activePrompt) {
            setErrorDialogMsg("Please choose a prompt.")
            return;
        }

        // check that coordinate fields are populated
        if (selectedCoords.lat == "" || selectedCoords.lng == "") {
            setErrorDialogMsg("Please set a value for both Latitude and Longitude.");
            return;
        }

		const params = new URLSearchParams({
			lat: selectedCoords.lat,
			long: selectedCoords.lng,
		});

		try {
            const res = await fetch(`${API_BASE}/api/location-data/?${params.toString()}`);

            if (!res.ok) {
                const errorJson = await res.json();
                throw new Error(errorJson.detail);
            }
        
            const json = await res.json();
            setLocationData(json);
            setCurrentTab("datadisplay");
		} catch (err) {
			console.error(err.message);
            if (err.message == "County not found using Geopy Nominatim") {
                setErrorDialogMsg(`Unable to fetch data for the selected
                    coordinates. Please pick a different location on the map.`);
            }
		}
	}


  return (
    <>
        {errorDialogMsg &&
            <ErrorDialog 
                message={errorDialogMsg}
                onClose={() => setErrorDialogMsg("")}
            />
        }

        <Flex h="100%" p="10px" gap="30px">
            <PromptSidebar
                activePrompt={activePrompt}
                setActivePrompt={setActivePrompt}
                fetchLocationData={fetchLocationData}
            />

                <Tabs.Root 
                    value={currentTab}
                    onValueChange={(e) => setCurrentTab(e.value)}
                    flex="1"
                    display="flex"
                    flexDirection="column"
                >
                    <Tabs.List>
                        <Tabs.Trigger value="map">
                            <LuMap /> Map
                        </Tabs.Trigger>
                        <Tabs.Trigger value="datadisplay">
                            <LuChartColumn /> Data Display
                        </Tabs.Trigger>
                    </Tabs.List>
                    <Tabs.Content value="map" flex="1" display="flex" minH="0px">
                        <InteractiveMap
                            selectedCoords={selectedCoords}
                            setSelectedCoords={setSelectedCoords}
                            setErrorDialogMsg={setErrorDialogMsg}
                        />
                    </Tabs.Content>
                    <Tabs.Content value="datadisplay" flex="1" display="flex" minH="0px">
                        <DataDisplay
                            locationData={locationData}
                            selectedCoords={selectedCoords}
                        />
                    </Tabs.Content>
                </Tabs.Root>

        </Flex>
    </>
  );
};

export default MainContent;
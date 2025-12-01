import { act, useState } from "react";
import { Flex, Tabs } from "@chakra-ui/react";
import { LuChartColumn, LuMap } from "react-icons/lu";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "./InteractiveMap";
import DataDisplay from "./DataDisplay";
import ErrorDialog from "../CustomComponents/ErrorDialog";

// This is the main webpage content - everything below the header

const MainContent = () => {
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
			if (!res.ok) throw new Error("Error fetching location data:");
			const json = await res.json();
			setLocationData(json);
		} catch (err) {
			console.error(err);
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

                    <Tabs.Root defaultValue="map" flex="1" display="flex" flexDirection="column">
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
                            />
                        </Tabs.Content>
                    </Tabs.Root>

        </Flex>
    </>
  );
};

export default MainContent;
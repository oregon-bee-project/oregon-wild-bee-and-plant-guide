import { useState, useEffect } from "react";
import { Box, Flex, Tabs } from "@chakra-ui/react";
import { LuChartColumn, LuMap } from "react-icons/lu";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "./InteractiveMap";
import DataDisplay from "./DataDisplay";

// This is the main webpage content - everything below the header

const MainContent = () => {
  const [selectedCoords, setSelectedCoords] = useState({ lat: "", lng: "" });
	const [locationData, setLocationData] = useState(null);


	const fetchLocationData = async () => {
		const params = new URLSearchParams({
			lat: selectedCoords.lat,
			long: selectedCoords.lng,
		});

		try {
			const res = await fetch(`/api/location-data/?${params.toString()}`);
			if (!res.ok) throw new Error("Error fetching location data:");
			const json = await res.json();
			console.log(json);
			setLocationData(json);
		} catch (err) {
			console.error(err);
		}
	}


  return (
    <>
      <Flex h="100%" p="10px" gap="30px">
        <PromptSidebar />

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
							fetchLocationData={fetchLocationData}
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
import { useState, useEffect } from "react";
import { Flex } from "@chakra-ui/react";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "./InteractiveMap";
import DataDisplay from "./DataDisplay";

// This is the main webpage content - everything below the header

const MainContent = () => {
  const [selectedPage, setSelectedPage] = useState("Map Page");
  const [selectedCoords, setSelectedCoords] = useState({ lat: "", lng: "" });

	useEffect(() => {
    const fetchData = async () => {
			const params = new URLSearchParams({
				lat: selectedCoords.lat,
				long: selectedCoords.lng,
			});

      try {
        const res = await fetch(`/api/location-data?${params.toString()}`);
        if (!res.ok) throw new Error("Error fetching location data:");
        const json = await res.json();
				console.log(json);
				//setData(json);
      } catch (err) {
        console.error(err);
      }
    }
    fetchData();

	}, [selectedCoords]);


  return (
    <>
      <Flex h="100%" p="10px" gap="30px">
        <PromptSidebar
          selectedPage={selectedPage}
          setSelectedPage={setSelectedPage}
        />
        {selectedPage == "Map Page" ? (
            <InteractiveMap
							selectedCoords={selectedCoords}
							setSelectedCoords={setSelectedCoords}
            />
        ) : (
            <DataDisplay />
        )}
      </Flex>
    </>
  );
};

export default MainContent;
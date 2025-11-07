import { useState } from "react";
import { Flex } from "@chakra-ui/react";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "./InteractiveMap";
import DataDisplay from "./DataDisplay";

// This is the main webpage content - everything below the header

const MainContent = () => {
  const [selectedPage, setSelectedPage] = useState("Map Page");

  return (
    <>
      <Flex h="100%" p="10px" gap="30px">
        <PromptSidebar
          selectedPage={selectedPage}
          setSelectedPage={setSelectedPage}
        />
        {selectedPage == "Map Page" ? <InteractiveMap /> : <DataDisplay />}
      </Flex>
    </>
  );
};

export default MainContent;
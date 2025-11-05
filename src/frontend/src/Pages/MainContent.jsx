import { Flex } from "@chakra-ui/react";
import PromptSidebar from "../CustomComponents/PromptSidebar";
import InteractiveMap from "../CustomComponents/InteractiveMap";

// This is the main webpage content - everything below the header

const MainContent = () => {
  return (
    <>
      <Flex h="100%" p="10px" gap="30px">
        <PromptSidebar />
        <InteractiveMap />
      </Flex>
    </>
  );
};

export default MainContent;
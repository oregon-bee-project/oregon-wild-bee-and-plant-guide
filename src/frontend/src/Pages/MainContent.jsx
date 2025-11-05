import { Flex } from "@chakra-ui/react";
import PromptSidebar from "../CustomComponents/PromptSidebar";

// This is the main webpage content - everything below the header

const MainContent = () => {
  return (
    <>
      <Flex h="100%" p="10px">
        <PromptSidebar />
      </Flex>
    </>
  );
};

export default MainContent;
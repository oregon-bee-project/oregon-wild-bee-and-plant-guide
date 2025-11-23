import { Box, Flex } from '@chakra-ui/react';
import OSUHeader from './CustomComponents/OSUHeader'
import MainContent from './Pages/MainContent';

const App = () => {

  return (
    <>
      <Flex direction="column" h="100vh">
        <OSUHeader />
        <Box flex="1" minH="0px">
          <MainContent />
        </Box>
      </Flex>
    </>
  )
}

export default App;

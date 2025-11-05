import { Box, Flex } from '@chakra-ui/react';
import { useState } from 'react'
import OSUHeader from './CustomComponents/OSUHeader'
import MainContent from './Pages/MainContent';

const App = () => {
  const [count, setCount] = useState(0);

  return (
    <>
      <Flex direction="column" minH="100vh">
        <OSUHeader />
        <Box flex="1" overflowY="auto">
          <MainContent />
        </Box>
      </Flex>
    </>
  )
}

export default App;

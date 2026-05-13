import {
  Box,
  Flex,
  Image,
  Text,
  Link,
  Stack,
  Button
} from '@chakra-ui/react';
import OSULogo from "@/assets/OSU-logo.png"
import '@/index.css'
import InfoDialog from './InfoDialog';

const OSUHeader = () => {
  return (
    <Box
      as="header"
      width="100%"
      minH={{ base: "200px", md: "144px" }}
      maxH={{ base: "200px", md: "144px" }}
      display="flex"
      flexDirection="column"
      bg="#000000"
      borderTop="12px solid #d73f09"
      borderBottom="1px solid #d73f09"
      m={0}
      p={0}
    >
      <Flex
        align={{base: "left", md: "center"}}
        flex="1"
        direction={{ base: "column", md: "row" }}
        textAlign={{ base: "center", md: "left" }}
      >
        {/* OSU Logo */}
        <Link
          href="https://oregonstate.edu/"
          target="_blank"
          rel="noopener noreferrer"
          _focus={{ outline: 'none' }}
          _focusVisible={{ outline: '1px solid white', outlineOffset: '2px' }}
        >
          <Image
            src={OSULogo}
            alt="Oregon State University Logo"
            width={{ base: "200px", md: "250px" }}
            mt={{ base: "5px", md: "0"}}
            ml={{ base: "20px", md: "52px" }}
            mr={{ base: "0", md: "19px" }}
            mb={{ base: "10px", md: "0" }}
          />
        </Link>

        {/* vertical separator - hidden on mobile */}
        <Box
          h={{ base: "1px", md: "100%" }}
          w={{ base: "100%", md: "1px" }}
          bg="#666666"
          display={{ base: "none", md: "block" }}
        />

        {/* title text */}
        <Box pl={{ base: "20px", md: "20px" }}>
          <Stack spacing={0} pb={{ base: "5px", md: "10px" }}>
          <Link
              href="https://agsci.oregonstate.edu/"
              target="_blank"
              rel="noopener noreferrer"
              _hover={{
                textDecoration: "underline",
                textDecorationColor: "white"
              }}
              _focus={{ outline: 'none' }}
              _focusVisible={{ outline: '1px solid white', outlineOffset: '2px' }}
            >
              <Text
                fontSize={{ base: "12px", md: "16px" }}
                fontFamily="Stratum2Light"
                fontWeight="600"
                textTransform="uppercase"
                letterSpacing="1px"
                color="white"
              >
                COLLEGE OF AGRICULTURAL SCIENCES{" "}
                <Text as="span" fontSize={{ base: "12px", md: "16px" }} color="#666666">»</Text>
              </Text>
            </Link>
            <Text
                fontSize={{ base: "18px", md: "24px" }}
                fontFamily="Stratum2Light"
                fontWeight="600"
                textTransform="uppercase"
                letterSpacing="1px"
                lineHeight="0.5"
                color="white"
              >
                OREGON WILD BEE AND PLANT GUIDE
            </Text>
          </Stack>
        </Box>
        <Box 
          ml={{ base: "0", md: "auto" }} 
          mr={{ base: "0", md: "50px" }}
          mt={{ base: "10px", md: "0" }}
        >
          <InfoDialog />
        </Box>
      </Flex>
    </Box>
  );
};

export default OSUHeader;

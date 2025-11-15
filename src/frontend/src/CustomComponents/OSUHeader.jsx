import {
  Box,
  Flex,
  Image,
  Text,
  Link,
  Stack
} from '@chakra-ui/react';
import OSULogo from "@/assets/OSU-logo.png"
import '@/index.css'

const OSUHeader = () => {
  return (
    <Box
      as="header"
      width="100%"
      minH="144px"
      maxH="144px"
      display="flex"
      flexDirection="column"
      bg="#000000"
      borderTop="12px solid #d73f09"
      borderBottom="1px solid #d73f09"
      m={0}
      p={0}
    >
      <Flex
        align="center"
        flex="1"
      >
        {/* OSU Logo */}
        <Image
          src={OSULogo}
          alt="Oregon State University Logo"
          width="250px"
          ml="52px"
          mr="19px"
        />

        {/* vertical separator */}
        <Box
          h="100%"
          w="1px"
          bg="#666666"
        />

        {/* title text */}
        <Box pl="20px">
          <Stack spacing={0}>
          <Link
              href="https://agsci.oregonstate.edu/"
              _hover={{ 
                textDecoration: "underline",
                textDecorationColor: "white"
              }}
            >
              <Text 
                fontSize="16px"
                fontFamily="Stratum2Regular"
                fontWeight="400"
                letterSpacing="1px"
                color="white"
              >
                COLLEGE OF AGRICULTURAL SCIENCES{" "}
                <Text as="span" fontSize="16px" color="#666666">»</Text>
              </Text>
            </Link>

            <Link
              href="https://agsci.oregonstate.edu/bee-atlas"
              _hover={{ 
                textDecoration: "underline",
                textDecorationColor: "white"
              }}
            >
              <Text 
                fontSize="24px"
                fontFamily="Stratum2Regular"
                fontWeight="400"
                letterSpacing="1px"
                lineHeight="0.5"
                color="white"
              >
                OREGON BEE ATLAS
              </Text>
            </Link>
          </Stack>
        </Box>
      </Flex>
    </Box>
  );
};

export default OSUHeader;
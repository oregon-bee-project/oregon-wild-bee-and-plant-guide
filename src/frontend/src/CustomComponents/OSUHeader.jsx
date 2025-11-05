import {
  Box,
  Flex,
  Image,
  Text,
  Link,
  HStack,
  Spacer,
} from '@chakra-ui/react';
import OSULogo from "@/assets/OSU-logo.png"
import { LuSearch } from "react-icons/lu";

const OSUHeader = () => {
  return (
    <Box>
      {/* top orange bar */}
      <Box bg="#d73f09" h="12px" />

      {/* main black bar */}
      <Flex
        as="header"
        align="center"
        bg="black"
        color="white"
        py={8}
        px={{ base: 4, md: 8 }}
        minH="90px"
      >
        {/* OSU Logo */}
        <Image
          src={OSULogo}
          alt="Oregon State University Logo"
          height="55px"
          mr={6}
        />

        {/* vertical separator */}
        <Box
          h="70px"
          w="1px"
          bg="gray.400"
          mr={6}
        />

        {/* title text */}
        <Box>
          <Text
            fontSize="xs"
            fontWeight="normal"
            color="white"
          >
            COLLEGE OF AGRICULTURAL SCIENCES
          </Text>
          <Text
            fontSize="2xl"
            fontWeight="bold"
            letterSpacing="wide"
            color="white"
          >
            OREGON BEE ATLAS
          </Text>
        </Box>

        <Spacer /> {/* pushes search/apply/myCAS to the right */}

        {/* right side links */}
        <HStack spacing={6} alignItems="center">
          <LuSearch
            color="#d73f09"
          />

          <Box
            h="15px"
            w="1px"
            bg="gray.400"
          />

          {/* apply link */}
          <Link
            href="#"
            color="white"
            fontSize="md"
            fontWeight="semibold"
            _hover={{ textDecoration: 'underline' }}
          >
            Apply
          </Link>

          <Box
            h="15px"
            w="1px"
            bg="gray.400"
          />

          {/* MyCAS link */}
          <Link
            href="#"
            color="white"
            fontSize="md"
            fontWeight="semibold"
            _hover={{ textDecoration: 'underline' }}
          >
            MyCAS
          </Link>
        </HStack>
      </Flex>
    </Box>
  );
};

export default OSUHeader;
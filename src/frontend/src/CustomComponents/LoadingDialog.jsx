import { useMemo } from "react";
import { Dialog, Portal, Box, Text } from "@chakra-ui/react";
import { keyframes } from "@emotion/react";
import { BEE_FUN_FACTS } from "./beeFunFacts";

const beeAnimation = keyframes`
  0% {
    transform: translateX(-15px);
  }
  50% {
    transform: translateX(15px);
  }
  100% {
    transform: translateX(-15px);
  }
`;

const pickRandomFact = () =>
    BEE_FUN_FACTS[Math.floor(Math.random() * BEE_FUN_FACTS.length)];

const LoadingDialog = ({ isOpen, title }) => {
    const randomFact = useMemo(pickRandomFact, [isOpen]);

    const isBeeFact = title == null;

    return (
        <Dialog.Root
            open={isOpen}
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Body
                            display="flex"
                            flexDirection="column"
                            alignItems="center"
                            justifyContent="center"
                            gap={2}
                            py={6}
                        >
                            <Box
                                width="60px"
                                height="60px"
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                                animation={`${beeAnimation} 1s linear infinite`}
                            >
                                <Text fontSize="3xl" aria-label="bee">
                                    🐝
                                </Text>
                            </Box>
                            {isBeeFact ? (
                                <>
                                    <Dialog.Title
                                        fontSize="lg"
                                        fontWeight="semibold"
                                        textAlign="center"
                                        px={2}
                                    >
                                        Did you know?
                                    </Dialog.Title>
                                    <Text
                                        fontSize="sm"
                                        fontStyle="italic"
                                        textAlign="center"
                                        px={2}
                                        color="fg.muted"
                                    >
                                        {randomFact}
                                    </Text>
                                </>
                            ) : (
                                <Dialog.Title
                                    fontSize="lg"
                                    fontWeight="medium"
                                    textAlign="center"
                                    px={2}
                                >
                                    {title}
                                </Dialog.Title>
                            )}
                        </Dialog.Body>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

export default LoadingDialog;
import ThumbnailForm from '../../../components/FileInputForms/ThumbnailForm';
import MenuForm from '../../../components/FileInputForms/MenuForm';
import {
  Alert,
  AlertIcon,
  Box,
  Button,
  HStack,
  Heading,
  VStack,
  useBreakpointValue
} from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import EateryDescriptionTag from '../../../components/EateryDescriptionTag';
import { useEffect, useRef, useState } from 'react';

const EditEaterySubPage = () => {
  const updateDescriptionTagRef = useRef<HTMLButtonElement>(null);
  const updateMenuRef = useRef<HTMLButtonElement>(null);
  const updateThumbnailRef = useRef<HTMLButtonElement>(null);

  const [submitted, setSubmitted] = useState(false);
  const [changesSaved, setChangesSaved] = useState(false);

  const stackDirection = useBreakpointValue({ base: 'column', md: 'row' });

  const handleSubmit = () => {
    if (updateDescriptionTagRef.current !== null) {
      updateDescriptionTagRef.current.click();
    }

    if (updateMenuRef.current !== null) {
      updateMenuRef.current.click();
    }

    if (updateThumbnailRef.current !== null) {
      updateThumbnailRef.current.click();
    }
  };

  useEffect(() => {
    if (submitted) {
      console.log('received');
      setChangesSaved(true);
      setTimeout(() => {
        setChangesSaved(false);
        setSubmitted(false);
      }, 3500);
    }
  }, [submitted]);

  return (
    <>
      <Box flex={1} bg="chowdownPurple.50" px={8} py={8}>
        {stackDirection === 'column' ? (
          <VStack gap={5} height="100%">
            <HStack w="100%" justifyContent="space-between">
              <Heading color="chowdown.gray">Edit Eatery</Heading>
              <Button
                colorScheme="chowdownGray"
                padding={5}
                onClick={handleSubmit}>
                Save changes
              </Button>
            </HStack>
            <VStack
              alignItems="flex-start"
              flex={1}
              bg="white"
              borderRadius="lg"
              px={5}
              py={5}
              width="100%">
              {changesSaved && (
                <Alert status="success">
                  <AlertIcon />
                  Changes have been saved!
                </Alert>
              )}

              <VStack w="100%" alignItems="flex-start" gap="4">
                <Heading size="md">Menu</Heading>
                <MenuForm
                  ref={updateMenuRef}
                  submitted={() => setSubmitted(true)}
                />
                <EateryDescriptionTag
                  ref={updateDescriptionTagRef}
                  submitted={() => setSubmitted(true)}
                />
                <ThumbnailForm
                  ref={updateThumbnailRef}
                  submitted={() => setSubmitted(true)}
                />
              </VStack>
            </VStack>
            <Outlet />
          </VStack>
        ) : (
          <VStack gap={10} height="100%">
            <HStack w="100%" justifyContent="space-between">
              <Heading color="chowdown.gray">Edit Eatery</Heading>
              <Button
                colorScheme="chowdownGray"
                padding={8}
                onClick={handleSubmit}>
                Save changes
              </Button>
            </HStack>
            <VStack
              alignItems="flex-start"
              flex={1}
              bg="white"
              borderRadius="lg"
              px={8}
              py={5}
              width="100%">
              {changesSaved && (
                <Alert status="success">
                  <AlertIcon />
                  Changes have been saved!
                </Alert>
              )}
              <HStack w="100%" alignItems="flex-start" gap="20">
                <VStack alignItems="flex-start" w="50%">
                  <Heading size="md">Menu</Heading>
                  <MenuForm
                    ref={updateMenuRef}
                    submitted={() => setSubmitted(true)}
                  />
                  <EateryDescriptionTag
                    ref={updateDescriptionTagRef}
                    submitted={() => setSubmitted(true)}
                  />
                </VStack>
                <VStack
                  alignItems="flex-start"
                  w="50%"
                  verticalAlign="top"
                  align="flex-start">
                  <ThumbnailForm
                    ref={updateThumbnailRef}
                    submitted={() => setSubmitted(true)}
                  />
                </VStack>
              </HStack>
            </VStack>
            <Outlet />
          </VStack>
        )}
      </Box>
    </>
  );
};

export default EditEaterySubPage;

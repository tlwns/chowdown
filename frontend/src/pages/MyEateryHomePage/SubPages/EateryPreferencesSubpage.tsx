import { Box, Button, Flex, Heading, VStack } from '@chakra-ui/react';
import { useRef } from 'react';
import EateryPersonalDetailsForm from '../../../components/EateryPersonalDetailsForm';

const EditPreferencesSubPage = () => {
  const saveChangesRef = useRef<HTMLButtonElement>(null);

  const handleSubmit = () => {
    if (saveChangesRef.current !== null) {
      saveChangesRef.current.click();
    }
  };

  return (
    <>
      <Box
        flex={1}
        bg="chowdownPurple.50"
        px={{ base: 4, md: 14 }}
        py={{ base: 4, md: 10 }}>
        <VStack gap={10} height="100%">
          <Flex
            w="100%"
            align={'center'}
            flexDir={{ base: 'column', md: 'row' }}
            gap={{ base: 4, md: 0 }}
            justifyContent="space-between">
            <Heading color="chowdown.gray">Eatery Details</Heading>
            <Button
              colorScheme="chowdownGray"
              padding={{ base: 4, md: 8 }}
              onClick={handleSubmit}>
              Save changes
            </Button>
          </Flex>
          <VStack
            flex={1}
            bg="white"
            borderRadius="lg"
            px={{ base: 4, md: 0 }}
            py={[5, 10, 20]}
            width="100%">
            <VStack w={{ md: '40%' }} alignItems="flex-start" gap="20">
              <EateryPersonalDetailsForm ref={saveChangesRef} />
            </VStack>
          </VStack>
        </VStack>
      </Box>
    </>
  );
};

export default EditPreferencesSubPage;

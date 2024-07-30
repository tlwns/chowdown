import { Box, Button, Flex, Heading, VStack } from '@chakra-ui/react';
import { useRef } from 'react';
import CustomerPersonalDetailsForm from '../../components/CustomerPersonalDetailsForm';

const MyAccountPage = () => {
  const saveChangesRef = useRef<HTMLButtonElement>(null);

  const handleSubmit = () => {
    if (saveChangesRef.current !== null) {
      saveChangesRef.current.click();
    }
  };

  return (
    <>
      <Box
        bg="chowdownPurple.50"
        px={{ base: 4, md: 14 }}
        py={{ base: 4, md: 10 }}
        height="100%"
        flex={1}>
        <VStack gap={10} height="100%">
          <Flex
            width={'100%'}
            align={'center'}
            justifyContent="space-between"
            flexDir={{ base: 'column', md: 'row' }}
            gap={{ base: 4, md: 0 }}>
            <Heading color="chowdown.gray">My Account</Heading>
            <Button
              colorScheme="chowdownGray"
              padding={{ base: 4, md: 8 }}
              onClick={handleSubmit}>
              Save changes
            </Button>
          </Flex>
          <VStack
            alignItems="center"
            justifyContent="center"
            bg="white"
            borderRadius="lg"
            flex={1}
            py={[5, 10, 20]}
            width="100%">
            <VStack px={{ base: 4, md: 0 }}>
              <CustomerPersonalDetailsForm ref={saveChangesRef} />
            </VStack>
          </VStack>
        </VStack>
      </Box>
    </>
  );
};

export default MyAccountPage;

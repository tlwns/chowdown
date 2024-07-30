import {
  VStack,
  Heading,
  Text,
  Flex,
  Icon,
  Tag,
  TagLabel,
  HStack
} from '@chakra-ui/react';
import { getEateryDetails } from '../../../utils/api/eateries';
import { useContext } from 'react';
import { AuthContext } from '../../../context/authContext';
import { useQuery } from '@tanstack/react-query';
import LoadingPage from '../../LoadingPage';
import { BiMap, BiPhone } from 'react-icons/bi';

const AboutUsSubPage = () => {
  const { getters } = useContext(AuthContext);
  const { userId: eateryId, sessionToken } = getters;

  const {
    data: details,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', eateryId, 'details'],
    queryFn: () => getEateryDetails(sessionToken!, eateryId!)
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <VStack
        boxShadow={'md'}
        alignItems="flex-start"
        w={'100%'}
        flex={1}
        bg="white"
        borderRadius="lg"
        px={8}
        py={6}
        gap={6}>
        <Heading>About Us</Heading>
        <VStack align={'flex-start'} w="100%">
          <Text fontSize="lg">{details.description}</Text>
          <Flex align={'center'}>
            <Icon as={BiMap} boxSize={'5'} />
            <Text fontSize="lg" ml={4}>
              {details.address.formatted_str}
            </Text>
          </Flex>
          <Flex align={'center'}>
            <Icon as={BiPhone} boxSize={'5'} />
            <Text fontSize="lg" ml={4}>
              {details.phone_number}
            </Text>
          </Flex>
        </VStack>
        <HStack>
          {details.keywords.map((label) => (
            <Tag
              size="lg"
              key={label}
              borderRadius="full"
              variant="solid"
              bg="chowdown.purple">
              <TagLabel>{label}</TagLabel>
            </Tag>
          ))}
        </HStack>
      </VStack>
    )
  );
};

export default AboutUsSubPage;

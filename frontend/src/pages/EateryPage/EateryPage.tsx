import { Box, Button, Flex, Heading, VStack, Image } from '@chakra-ui/react';
import { Outlet, useLocation, useParams } from 'react-router-dom';

import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getEateryPublicDetails } from '../../utils/api/eateries';
import LoadingPage from '../LoadingPage';

const EateryPage = () => {
  //  Get which child route is being rendered (subpage of eatery page)
  const { pathname } = useLocation();
  const subPageDisplaying = pathname.split('/').pop();
  const { eateryId } = useParams();

  const {
    data: details,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', parseInt(eateryId!), 'details', 'public'],
    queryFn: () => getEateryPublicDetails(parseInt(eateryId!))
  });

  const subPages = [
    ['about-us', 'About us'],
    ['vouchers', 'Vouchers'],
    ['menu', 'Menu'],
    ['reviews', 'Reviews']
  ];

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <VStack flex={1} bg="chowdownPurple.50" pb={10}>
        <VStack height="100%" pb={6} maxW={'4xl'} width={'100%'}>
          <Box height={40} width={'100%'} px={{ base: 0, md: 14 }}>
            <Image
              src={details.thumbnail_uri}
              alt={`${details.name}'s thumbnail image`}
              width={'100%'}
              height={'100%'}
              borderBottomRadius={{ base: '0', md: '10' }}
              fit={'cover'}
            />
          </Box>
          <Flex
            mt={{ base: 4, md: 0 }}
            px={{ base: 6, md: 14 }}
            flexDir={{ base: 'column', md: 'row' }}
            w="100%"
            justifyContent="space-between"
            align="center"
            position={{ base: 'static', md: 'sticky' }}
            height={{ base: 'auto', md: '24' }}
            mb={{ base: 4, md: 0 }}
            width={'100%'}
            bg={'chowdownPurple.50'}
            top={20}>
            <Heading>{details.name}</Heading>
            <Flex
              pt={{ base: 4, md: 0 }}
              flexWrap={'wrap'}
              display={'flex'}
              justifyContent={'center'}
              gap={2}
              alignItems={'center'}>
              {/* Subpage buttons */}
              {subPages.map(([route, label]) => (
                <Button
                  as={Link}
                  to={route}
                  key={route}
                  width={100}
                  colorScheme={
                    subPageDisplaying === route ? 'chowdownGray' : undefined
                  }
                  borderRadius="full">
                  {label}
                </Button>
              ))}
            </Flex>
          </Flex>
          {/* Subpages */}
          <Box width={'100%'} px={{ base: 6, md: 14 }} flex={1}>
            <Outlet />
          </Box>
        </VStack>
      </VStack>
    )
  );
};

export default EateryPage;

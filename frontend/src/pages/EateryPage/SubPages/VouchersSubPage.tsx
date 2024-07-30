import { Flex, Text, VStack } from '@chakra-ui/react';

import Voucher from '../../../components/Vouchers/Voucher';
import { getEateryVouchers } from '../../../utils/api/eateries';
import { useParams } from 'react-router-dom';
import LoadingPage from '../../LoadingPage';
import React from 'react';
import { useQuery } from '@tanstack/react-query';

const VouchersSubPage = () => {
  const { eateryId } = useParams();

  const {
    data: vouchers,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', parseInt(eateryId!), 'vouchers'],
    queryFn: () => getEateryVouchers(parseInt(eateryId!)),
    select: (data) => {
      return data.vouchers.map(
        (voucher) =>
          ({
            id: voucher.voucher_id,
            name: voucher.name,
            description: voucher.description,
            conditions: voucher.conditions,
            expiry: voucher.expiry,
            totalQuantity: voucher.total_quantity,
            unclaimedQuantity: voucher.unclaimed_quantity,
            eatery_id: parseInt(eateryId!)
          }) satisfies React.ComponentProps<typeof Voucher>
      );
    }
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <VStack w="100%" h={'100%'} gap={5}>
        {vouchers.length !== 0 ? (
          <>
            {vouchers.map((voucher) => (
              <Voucher key={voucher.id} {...voucher} />
            ))}
          </>
        ) : (
          <Flex
            width={'100%'}
            boxShadow={'md'}
            bg="white"
            borderRadius="lg"
            px={8}
            justify="center"
            py={6}>
            <Text fontSize="lg">
              Sorry! No vouchers available at the moment 😔
            </Text>
          </Flex>
        )}
      </VStack>
    )
  );
};

export default VouchersSubPage;

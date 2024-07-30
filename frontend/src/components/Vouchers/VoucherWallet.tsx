import { useQuery } from '@tanstack/react-query';
import { Flex, Text } from '@chakra-ui/react';

import { getCustomerVouchers } from '../../utils/api/customers';
import React, { useContext } from 'react';
import { AuthContext } from '../../context/authContext';
import LoadingPage from '../../pages/LoadingPage';
import VoucherCard from './VoucherCard';

type VoucherWalletProps = {
  filter: string[];
};

const VoucherWallet: React.FC<VoucherWalletProps> = ({ filter }) => {
  const { getters } = useContext(AuthContext);
  const { userId: customerId, sessionToken } = getters;

  const {
    data: vouchers,
    isLoading: isLoadingVouchers,
    isSuccess
  } = useQuery({
    queryKey: [customerId, 'vouchers'],
    queryFn: () => getCustomerVouchers(sessionToken!, customerId!),
    select: (data) =>
      data.vouchers
        .map((voucher) => {
          // rename keys to camelCase
          return {
            voucherId: voucher.voucher_id,
            voucherInstanceId: voucher.voucher_instance_id,
            eateryId: voucher.eatery_id,
            name: voucher.name,
            description: voucher.description,
            conditions: voucher.conditions,
            expiry: voucher.expiry,
            status: voucher.status,
            givenRating: voucher.given_rating
          };
        })
        .filter((voucher) => filter.includes(voucher.status))
  });

  if (isLoadingVouchers) {
    return <LoadingPage />;
  }

  return (
    isSuccess &&
    (vouchers.length !== 0 ? (
      <Flex
        w={'100%'}
        justify={'center'}
        fontWeight={'semibold'}
        gap={10}
        flexWrap={'wrap'}>
        {vouchers.map((voucher) => (
          <VoucherCard
            key={voucher.voucherInstanceId}
            voucherInstanceId={voucher.voucherInstanceId}
            status={voucher.status}
            name={voucher.name}
            description={voucher.description}
            conditions={voucher.conditions}
            expiry={voucher.expiry}
            eateryId={voucher.eateryId}
            givenRating={voucher.givenRating}
          />
        ))}
      </Flex>
    ) : (
      <Flex
        width={'100%'}
        boxShadow={'md'}
        bg="white"
        borderRadius="lg"
        justify="center"
        px={8}
        py={6}>
        <Text fontSize="lg">You haven&apos;t claimed any vouchers yet 😔</Text>
      </Flex>
    ))
  );
};

export default VoucherWallet;

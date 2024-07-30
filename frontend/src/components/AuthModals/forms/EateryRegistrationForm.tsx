import React, { useState } from 'react';
import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  VStack,
  Text,
  Flex,
  VisuallyHidden
} from '@chakra-ui/react';
import { eateryRegister } from '../../../utils/api/auth';
import { SubmitHandler, useForm } from 'react-hook-form';

import * as requirements from './requirements';
import { AxiosError } from 'axios';
import { CommonFormProps } from '../types';
import AddressInput from '../../AddressInput';

type FormValues = {
  email: string;
  password: string;
  confirmPassword: string;
  businessName: string;
  firstName: string;
  lastName: string;
  address: string;
  abn: string;
  phoneNumber: string;
  unitNumber: string;
};

const defaultValues: FormValues = {
  email: '',
  password: '',
  confirmPassword: '',
  firstName: '',
  lastName: '',
  address: '',
  abn: '',
  businessName: '',
  phoneNumber: '',
  unitNumber: ''
};

const EateryRegistrationForm: React.FC<CommonFormProps> = ({
  onSubmitError,
  onSubmitSuccess
}) => {
  const {
    handleSubmit,
    register,
    setError,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>();

  const [fullAddress, setFullAddress] = useState<GeoDataResponse | undefined>();

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    try {
      if (!fullAddress) {
        throw new Error('error missing... Should not be reachable');
      }

      const res = await eateryRegister({
        email: data.email,
        password: data.password,
        abn: data.abn,
        business_name: data.businessName,
        manager_first_name: data.firstName,
        manager_last_name: data.lastName,
        phone_number: data.phoneNumber,
        address: {
          city: fullAddress.city ?? '',
          country: fullAddress.country,
          county: fullAddress.county ?? '',
          fmt_address: fullAddress.formatted,
          house_number: fullAddress.house_no ?? '',
          latitude: fullAddress.lat,
          longitude: fullAddress.lon,
          postcode: fullAddress.postcode ?? '',
          state: fullAddress.state,
          street: fullAddress.street ?? '',
          unit_number: data.unitNumber
        }
      });
      onSubmitSuccess(res);
    } catch (e) {
      const error = e as AxiosError<{ detail: string }>;
      setError('root', { message: `${error.response?.data?.detail}` }); // TODO
      reset(defaultValues, { keepErrors: true });
      setFullAddress(undefined);
      onSubmitError(e);
    }
  };

  const { name: addressFieldName, onBlur: addressFieldOnBlur } = register(
    'address',
    requirements.registration.address
  );

  return (
    <VStack spacing="4" as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.email}>
        <FormLabel>Business Email</FormLabel>
        <Input
          type="email"
          placeholder="name@domain.com"
          {...register('email', requirements.registration.email)}
        />
        <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.password}>
        <FormLabel>Password</FormLabel>
        <Input
          type="password"
          placeholder="Password"
          {...register('password', requirements.registration.password)}
        />
        <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.confirmPassword}>
        <Input
          type="password"
          placeholder="Repeat Password"
          {...register('confirmPassword', {
            ...requirements.registration.password,
            validate: (v) => {
              if (watch('password') !== v) return 'Passwords do not match';
            }
          })}
        />
        <FormErrorMessage>{errors.confirmPassword?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.businessName}>
        <FormLabel>Eatery Details</FormLabel>
        <Input
          placeholder="Business Name"
          {...register('businessName', requirements.registration.businessName)}
        />
        <FormErrorMessage>{errors.businessName?.message}</FormErrorMessage>
      </FormControl>

      <Flex gap="4">
        <FormControl
          isRequired
          isDisabled={isSubmitting}
          isInvalid={!!errors.firstName}>
          <FormLabel as={VisuallyHidden}>First Name</FormLabel>
          <Input
            placeholder="Manager First Name"
            {...register('firstName', requirements.registration.firstName)}
          />
          <FormErrorMessage>{errors.firstName?.message}</FormErrorMessage>
        </FormControl>

        <FormControl
          isRequired
          isDisabled={isSubmitting}
          isInvalid={!!errors.lastName}>
          <FormLabel as={VisuallyHidden}>Last Name</FormLabel>
          <Input
            placeholder="Manager Last Name"
            {...register('lastName', requirements.registration.lastName)}
          />
          <FormErrorMessage>{errors.lastName?.message}</FormErrorMessage>
        </FormControl>
      </Flex>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.address}>
        <FormLabel as={VisuallyHidden}>Eatery Address</FormLabel>
        <AddressInput
          onAddressChoice={(address) => {
            setValue(addressFieldName, address.formatted);
            setFullAddress(address);
          }}
          inputProps={{
            name: addressFieldName,
            onBlur: addressFieldOnBlur,
            placeholder: 'Eatery Address'
          }}
        />
        <FormErrorMessage>{errors.address?.message}</FormErrorMessage>
      </FormControl>

      <Flex gap="4">
        <FormControl
          flexShrink="3"
          isDisabled={isSubmitting}
          isInvalid={!!errors.unitNumber}>
          <FormLabel as={VisuallyHidden}>Unit Number (not required)</FormLabel>
          <Input
            placeholder="Unit No."
            {...register('unitNumber', requirements.registration.unitNumber)}
          />
          <FormErrorMessage>{errors.unitNumber?.message}</FormErrorMessage>
        </FormControl>

        <FormControl
          flexGrow="3"
          isRequired
          isDisabled={isSubmitting}
          isInvalid={!!errors.phoneNumber}>
          <FormLabel as={VisuallyHidden}>Phone Number</FormLabel>
          <Input
            type="tel"
            placeholder="Phone Number: +123-456-789-098"
            {...register('phoneNumber', requirements.registration.phoneNumber)}
          />
          <FormErrorMessage>{errors.phoneNumber?.message}</FormErrorMessage>
        </FormControl>
      </Flex>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.abn}>
        <FormLabel as={VisuallyHidden}>ABN</FormLabel>
        <Input
          type="number"
          placeholder="ABN (without spaces)"
          {...register('abn', requirements.registration.abn)}
        />
        <FormErrorMessage>{errors.abn?.message}</FormErrorMessage>
      </FormControl>

      {errors.root && (
        <Text variant="error" color="red">
          * {errors.root.message}
        </Text>
      )}

      <Button
        type="submit"
        colorScheme="chowdownLavender"
        borderRadius="full"
        isLoading={isSubmitting}>
        Register as Eatery
      </Button>
    </VStack>
  );
};

export default EateryRegistrationForm;

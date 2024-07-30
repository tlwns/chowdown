import {
  Button,
  Center,
  Flex,
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  Input,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Select,
  Switch,
  VStack
} from '@chakra-ui/react';
import { SubmitHandler, useForm } from 'react-hook-form';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import React, { useContext, useState } from 'react';
import { AuthContext } from '../../context/authContext';
import { createVoucher } from '../../utils/api/vouchers';
import * as requirements from './requirements';

type VoucherCreationFormProps = {
  onSubmitSuccess: () => void;
};

type FormValues = {
  name: string;
  description: string;
  conditions: string;
  quantity: number;
  release: string;
  expiry: string;
  schedule?: 'once' | 'daily' | 'weekly' | 'fortnightly' | 'monthly';
};

const defaultValues: FormValues = {
  name: '',
  description: '',
  conditions: '',
  quantity: 0,
  release: new Date().toISOString(), // Today TODO: Set release schedule
  expiry: '',
  schedule: undefined // TODO: Set scheduling
};

const getDateDifferenceAsISOString = (startDate: Date, endDate: Date) => {
  const durationInMs = Math.abs(endDate.getTime() - startDate.getTime());

  const milliseconds = durationInMs % 1000;
  const seconds = Math.floor((durationInMs / 1000) % 60);
  const minutes = Math.floor((durationInMs / (1000 * 60)) % 60);
  const hours = Math.floor((durationInMs / (1000 * 60 * 60)) % 24);
  const days = Math.floor(durationInMs / (1000 * 60 * 60 * 24));

  return `P${days}DT${hours}H${minutes}M${seconds}.${milliseconds}S`;
};

const VoucherCreationForm: React.FC<VoucherCreationFormProps> = ({
  onSubmitSuccess
}) => {
  const { getters } = useContext(AuthContext);
  const queryClient = useQueryClient();

  const [useSchedule, setSchedule] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({
    defaultValues
  });

  const { mutateAsync } = useMutation({
    mutationFn: (data: FormValues) =>
      createVoucher(getters.sessionToken!, {
        eatery_id: getters.userId!,
        name: data.name,
        description: data.description,
        conditions: data.conditions,
        quantity: data.quantity,
        release: data.release,
        duration: getDateDifferenceAsISOString(
          new Date(data.release),
          new Date(data.expiry)
        ),
        schedule: data.schedule === 'once' ? undefined : data.schedule
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['eatery', getters.userId!, 'vouchers']
      });
    }
  });

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    try {
      // react-hook-form's handleSubmit requires an async function that returns a promise or awaits a promise
      console.log(data);
      await mutateAsync({
        name: data.name,
        description: data.description,
        conditions: data.conditions,
        quantity: data.quantity,
        release: data.release,
        expiry: data.expiry,
        schedule: data.schedule
      });

      onSubmitSuccess();
    } catch (e) {
      // TODO
    }
  };

  return (
    <VStack as="form" spacing="4" onSubmit={handleSubmit(onSubmit)} pb={4}>
      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.name}>
        <FormLabel>Title</FormLabel>
        <Input
          type="text"
          placeholder="Taco Tuesday Special"
          {...register('name', requirements.creation.name)}
        />
        <FormErrorMessage>{errors.name?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.description}>
        <FormLabel>Description</FormLabel>
        <Input
          placeholder="Buy 2 Tacos, Get 1 Free"
          {...register('description', requirements.creation.description)}
        />
        <FormErrorMessage>{errors.description?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.conditions}>
        <FormLabel>Conditions</FormLabel>
        <Input
          placeholder="Valid only on Tuesdays"
          {...register('conditions', requirements.creation.conditions)}
        />
        <FormErrorMessage>{errors.conditions?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.quantity}>
        <FormLabel>Quantity</FormLabel>
        <NumberInput min={0}>
          <NumberInputField
            {...register('quantity', requirements.creation.quantity)}
          />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
        <FormErrorMessage>{errors.quantity?.message}</FormErrorMessage>
      </FormControl>

      <FormControl
        isRequired
        isDisabled={isSubmitting}
        isInvalid={!!errors.expiry}>
        <FormLabel>Expiry Date</FormLabel>
        <Input
          type="datetime-local"
          placeholder="Expiry Date"
          {...register('expiry', requirements.creation.expiry)}
        />
        <FormErrorMessage>{errors.expiry?.message}</FormErrorMessage>
      </FormControl>

      <Center>
        <FormLabel>Schedule Voucher</FormLabel>
        <Switch id="schedule" onChange={() => setSchedule(!useSchedule)} />
      </Center>

      {useSchedule && (
        <Flex gap={4}>
          <FormControl
            isRequired={useSchedule}
            isDisabled={isSubmitting}
            isInvalid={!!errors.schedule}>
            <FormLabel>Release Date</FormLabel>
            <Input
              type="datetime-local"
              placeholder="Release Date"
              {...register('release', requirements.creation.release)}
            />
            <FormErrorMessage>{errors.release?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isDisabled={isSubmitting} isInvalid={!!errors.schedule}>
            <FormLabel>Schedule</FormLabel>
            <Select
              defaultValue="once"
              {...register('schedule', requirements.creation.schedule)}>
              <option value="once">Once</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="fortnightly">Fortnightly</option>
              <option value="monthly">Monthly</option>
            </Select>
            <FormErrorMessage>{errors.schedule?.message}</FormErrorMessage>
          </FormControl>
        </Flex>
      )}

      <HStack>
        <Button
          type="submit"
          variant="outline"
          colorScheme="chowdownLavender"
          borderRadius="full"
          isLoading={isSubmitting}
          w={40}>
          Save and publish
        </Button>
      </HStack>
    </VStack>
  );
};

export default VoucherCreationForm;

import React from 'react';
import {
  Box,
  Flex,
  FlexProps,
  UseRadioGroupProps,
  UseRadioProps,
  useRadio,
  useRadioGroup
} from '@chakra-ui/react';
import { StarIcon } from '@chakra-ui/icons';

const StarRadio: React.FC<UseRadioProps & { extendRight?: boolean }> = (
  props
) => {
  // https://developer.mozilla.org/en-US/docs/Web/CSS/Subsequent-sibling_combinator
  // https://v2.chakra-ui.com/docs/styled-system/style-props#pseudo
  const { getInputProps, getRadioProps } = useRadio(props);

  const inputProps = getInputProps();
  const buttonProps = getRadioProps();

  return (
    <Box
      as="label"
      paddingRight={props.extendRight ? '1' : undefined}
      pointerEvents={props.isDisabled ? 'none' : undefined}
      cursor="pointer"
      data-peer
      color="gray.100"
      _checked={{
        color: 'yellow.400'
      }}
      _peerChecked={{
        color: 'yellow.400'
      }}
      _hover={{
        color: 'yellow.300 !important'
      }}
      _peerHover={{
        color: 'yellow.300 !important'
      }}
      {...buttonProps}>
      <StarIcon h="6" w="6" display="block" />
      <input {...inputProps} />
    </Box>
  );
};

type Options = '0' | '1' | '2' | '3' | '4' | '5';
type StarRatingInputProps = {
  defaultValue?: Options;
  value?: Options;
  name?: UseRadioGroupProps['name'];
  onChange?: (nextValue: Options) => void;
  isDisabled?: UseRadioGroupProps['isDisabled'];
  onBlur?: FlexProps['onBlur'];
};

export const StarRatingInput: React.FC<StarRatingInputProps> = ({
  defaultValue = '0',
  value,
  name,
  onChange,
  isDisabled,
  onBlur
}) => {
  // https://v2.chakra-ui.com/docs/components/radio
  const { getRootProps, getRadioProps } = useRadioGroup({
    defaultValue,
    value,
    onChange,
    isDisabled,
    name
  });

  const groupProps = getRootProps();

  return (
    <Flex {...groupProps} direction="row-reverse" bg="white" onBlur={onBlur}>
      {/* Reversed so the CSS works */}
      {['5', '4', '3', '2', '1'].map((value) => {
        const radioProps = getRadioProps({ value });
        return (
          <StarRadio
            key={value}
            extendRight={value !== '5'}
            isDisabled={isDisabled}
            {...radioProps}
          />
        );
      })}
    </Flex>
  );
};

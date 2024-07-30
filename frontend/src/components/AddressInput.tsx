import { useBoolean } from '@chakra-ui/react';
import {
  AutoComplete as AutoCompletePropless,
  AutoCompleteInput as AutoCompleteInputPropless,
  AutoCompleteItem as AutoCompleteItemPropless,
  AutoCompleteItemProps,
  AutoCompleteList,
  AutoCompleteProps,
  AutoCompleteInputProps
} from '@choc-ui/chakra-autocomplete';
import React, { useState } from 'react';
import { useDebouncedCallback } from 'use-debounce';
import { getAddressCompletion } from '../utils/api/other';

const AutoComplete: React.FC<AutoCompleteProps> = AutoCompletePropless;
const AutoCompleteInput: React.FC<AutoCompleteInputProps> =
  AutoCompleteInputPropless;
const AutoCompleteItem: React.FC<AutoCompleteItemProps> =
  AutoCompleteItemPropless;

type AddressInputProps = {
  onAddressChoice?: (address: GeoDataResponse) => void;
  inputProps?: AutoCompleteInputProps;
};

const AddressInput: React.FC<AddressInputProps> = ({
  inputProps,
  onAddressChoice
}) => {
  const [isDebouncing, { on: debouncingOn, off: debouncingOff }] =
    useBoolean(false);
  const [options, setOptions] = useState<Record<string, GeoDataResponse>>({});

  const updateInputValueDebounced = useDebouncedCallback(
    async (input: string) => {
      const completions = await getAddressCompletion(input);
      const newOptions = Object.fromEntries(
        completions.results.map((place) => [place.formatted, place])
      );
      setOptions(newOptions);
      debouncingOff();
    },
    1000,
    {
      trailing: true
    }
  );

  const startDebounce = (value: string) => {
    if (!isDebouncing) {
      debouncingOn();
    }
    updateInputValueDebounced(value);
  };

  const onChange = (value: string) => {
    if (onAddressChoice !== undefined) {
      onAddressChoice(options[value]);
    }
    setOptions({});
  };

  return (
    <AutoComplete disableFilter isLoading={isDebouncing} onChange={onChange}>
      <AutoCompleteInput
        {...inputProps}
        onInput={(e) => startDebounce(e.currentTarget.value)}
      />
      <AutoCompleteList>
        {Object.entries(options).map(([placeKey, place]) => (
          <AutoCompleteItem
            key={`option-${placeKey}`}
            value={placeKey}
            textTransform="capitalize">
            {place.formatted}
          </AutoCompleteItem>
        ))}
      </AutoCompleteList>
    </AutoComplete>
  );
};

export default AddressInput;

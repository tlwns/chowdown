import { SimpleGrid } from '@chakra-ui/react';

import React from 'react';
import EateryCard from './EateryCard';

import { EateryBrief } from '../types/eateryTypes';

type EateryAlbumProps = {
  eateries: EateryBrief[];
};

const EateryAlbum: React.FC<EateryAlbumProps> = ({ eateries }) => {
  return (
    <>
      <SimpleGrid minChildWidth={240} spacing={10}>
        {eateries.map((eatery) => (
          <EateryCard
            key={`eatery-card-${eatery.eateryId}`}
            eateryId={eatery.eateryId}
            eateryName={eatery.eateryName}
            numVouchers={eatery.numVouchers}
            topThreeVouchers={eatery.topThreeVouchers}
            thumbnailURI={eatery.thumbnailURI}
            averageRating={eatery.averageRating}
          />
        ))}
      </SimpleGrid>
    </>
  );
};

export default EateryAlbum;

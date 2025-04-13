
import {
  Box,
  Image,
  Badge,
  Text,
  Stack,
  useColorModeValue,
  Button,
  Flex,
  Icon,
  HStack,
} from '@chakra-ui/react';
import { StarIcon, ShoppingCartIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCart } from '../../context/CartContext';

interface ProductCardProps {
  id: string;
  name: string;
  category: string;
  image: string;
  price: number;
  rating: number;
  reviewCount: number;
  isNew?: boolean;
  isSale?: boolean;
  salePrice?: number;
}

const ProductCard = ({
  id,
  name,
  category,
  image,
  price,
  rating,
  reviewCount,
  isNew = false,
  isSale = false,
  salePrice
}: ProductCardProps) => {
  const { addItem } = useCart();

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    addItem({
      id,
      name,
      price: isSale && salePrice ? salePrice : price,
      image
    });
  };

  return (
    <Box
      as={Link}
      to={`/products/${id}`}
      borderWidth="1px"
      borderRadius="xl"
      overflow="hidden"
      p={4}
      bg={useColorModeValue('white', 'gray.800')}
      boxShadow="lg"
      transition="all 0.3s"
      _hover={{
        transform: 'translateY(-5px)',
        boxShadow: 'xl',
      }}
      position="relative"
      height="100%"
      display="flex"
      flexDirection="column"
    >
      {isNew && (
        <Badge
          borderRadius="full"
          px="2"
          colorScheme="green"
          position="absolute"
          top={2}
          left={2}
          zIndex={1}
        >
          New
        </Badge>
      )}
      {isSale && (
        <Badge
          borderRadius="full"
          px="2"
          colorScheme="red"
          position="absolute"
          top={isNew ? 10 : 2}
          left={2}
          zIndex={1}
        >
          Sale
        </Badge>
      )}

      <Box
        textAlign="center" 
        py={4} 
        position="relative" 
        height="200px"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Image 
          src={image} 
          alt={name} 
          objectFit="contain" 
          maxH="180px"
          mx="auto"
          transition="transform 0.3s ease"
          _hover={{ transform: 'scale(1.05)' }}
        />
      </Box>

      <Box pt={4} flex="1" display="flex" flexDirection="column">
        <Text color="gray.500" fontSize="sm" fontWeight="medium" mb={1}>
          {category}
        </Text>
        <Text
          mt={1}
          fontWeight="semibold"
          as="h4"
          lineHeight="tight"
          noOfLines={2}
          fontSize="md"
          color={useColorModeValue('gray.700', 'white')}
          mb={2}
          flex="1"
        >
          {name}
        </Text>
        
        <HStack mt={1} mb={2}>
          {Array(5)
            .fill('')
            .map((_, i) => (
              <StarIcon
                key={i}
                color={i < Math.round(rating) ? 'brand.400' : 'gray.300'}
                size={12}
              />
            ))}
          <Text ml={1} fontSize="sm" color="gray.500">
            ({reviewCount})
          </Text>
        </HStack>
        
        <Flex justify="space-between" align="center" mt="auto">
          <Box>
            {isSale && salePrice ? (
              <Flex align="center" direction="column" alignItems="flex-start">
                <Text
                  fontWeight="bold"
                  fontSize="lg"
                  color="red.500"
                >
                  ${salePrice.toFixed(2)}
                </Text>
                <Text
                  textDecoration="line-through"
                  color="gray.500"
                  fontSize="sm"
                >
                  ${price.toFixed(2)}
                </Text>
              </Flex>
            ) : (
              <Text fontWeight="bold" fontSize="lg" color="brand.500">
                ${price.toFixed(2)}
              </Text>
            )}
          </Box>
          
          <Button
            rounded="full"
            size="sm"
            color="white"
            bg="brand.500"
            _hover={{ bg: 'brand.600' }}
            leftIcon={<ShoppingCartIcon size={16} />}
            onClick={handleAddToCart}
            boxShadow="sm"
          >
            Add
          </Button>
        </Flex>
      </Box>
    </Box>
  );
};

export default ProductCard;


import { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Image,
  Flex,
  Grid,
  GridItem,
  Divider,
  IconButton,
  Input,
  FormControl,
  FormLabel,
  Select,
  useToast,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from '@chakra-ui/react';
import { ChevronRightIcon, MinusIcon, PlusIcon, ShoppingCartIcon, TrashIcon, XIcon } from 'lucide-react';
import { useCart } from '../context/CartContext';

const CartPage = () => {
  const { items, updateQuantity, removeItem, totalItems, totalPrice } = useCart();
  const toast = useToast();
  const [couponCode, setCouponCode] = useState('');

  const handleIncrement = (id: string, currentQty: number) => {
    updateQuantity(id, currentQty + 1);
  };

  const handleDecrement = (id: string, currentQty: number) => {
    if (currentQty > 1) {
      updateQuantity(id, currentQty - 1);
    }
  };

  const handleRemove = (id: string, name: string) => {
    removeItem(id);
    
    toast({
      title: 'Item removed',
      description: `${name} has been removed from your cart`,
      status: 'info',
      duration: 3000,
      isClosable: true,
      position: 'top-right',
    });
  };

  const handleApplyCoupon = () => {
    if (!couponCode) {
      toast({
        title: 'Error',
        description: 'Please enter a coupon code',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // In a real app, you would validate the coupon with your backend
    toast({
      title: 'Invalid coupon',
      description: 'The coupon code you entered is invalid',
      status: 'error',
      duration: 3000,
      isClosable: true,
    });
  };

  if (items.length === 0) {
    return (
      <Container maxW="container.xl" py={8}>
        <Breadcrumb separator={<ChevronRightIcon size={14} />} mb={8}>
          <BreadcrumbItem>
            <BreadcrumbLink as={RouterLink} to="/">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink>Cart</BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>
        
        <Box 
          py={10} 
          textAlign="center"
          bg="white"
          borderRadius="md"
          boxShadow="sm"
        >
          <ShoppingCartIcon size={64} color="#CBD5E0" style={{ margin: '0 auto 1rem' }} />
          <Heading size="lg" mb={4}>Your cart is empty</Heading>
          <Text color="gray.500" mb={6}>
            Looks like you haven't added any products to your cart yet.
          </Text>
          <Button 
            as={RouterLink}
            to="/products"
            colorScheme="brand"
            leftIcon={<ShoppingCartIcon size={18} />}
            size="lg"
          >
            Start Shopping
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Breadcrumb separator={<ChevronRightIcon size={14} />} mb={8}>
        <BreadcrumbItem>
          <BreadcrumbLink as={RouterLink} to="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>
          <BreadcrumbLink>Cart</BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>
      
      <Heading mb={6}>Shopping Cart ({totalItems} {totalItems === 1 ? 'item' : 'items'})</Heading>
      
      <Grid templateColumns={{ base: '1fr', lg: '3fr 1fr' }} gap={8}>
        {/* Cart Items */}
        <GridItem>
          <Box 
            bg="white" 
            borderRadius="md"
            boxShadow="sm"
            overflow="hidden"
          >
            {/* Header */}
            <Flex 
              bg="gray.50" 
              py={4} 
              px={6}
              fontWeight="bold"
              color="gray.600"
              display={{ base: 'none', md: 'flex' }}
            >
              <Box flex="2">Product</Box>
              <Box flex="1" textAlign="center">Price</Box>
              <Box flex="1" textAlign="center">Quantity</Box>
              <Box flex="1" textAlign="center">Total</Box>
              <Box w="40px"></Box>
            </Flex>
            
            {/* Items */}
            <VStack spacing={0} divider={<Divider />}>
              {items.map((item) => (
                <Flex 
                  key={item.id} 
                  py={4} 
                  px={6} 
                  alignItems="center"
                  direction={{ base: 'column', md: 'row' }}
                >
                  {/* Product */}
                  <Flex flex="2" alignItems="center" width={{ base: '100%', md: 'auto' }}>
                    <Image 
                      src={item.image} 
                      alt={item.name} 
                      boxSize="80px"
                      objectFit="cover"
                      borderRadius="md"
                    />
                    <Box ml={4}>
                      <Text fontWeight="semibold">{item.name}</Text>
                      <Text fontSize="sm" color="gray.500" display={{ md: 'none' }}>
                        ${item.price.toFixed(2)}
                      </Text>
                    </Box>
                  </Flex>
                  
                  {/* Price */}
                  <Box 
                    flex="1" 
                    textAlign={{ base: 'left', md: 'center' }}
                    mt={{ base: 2, md: 0 }}
                    ml={{ base: 'auto', md: 0 }}
                    display={{ base: 'none', md: 'block' }}
                  >
                    ${item.price.toFixed(2)}
                  </Box>
                  
                  {/* Quantity */}
                  <HStack 
                    flex="1" 
                    justifyContent={{ base: 'flex-start', md: 'center' }}
                    mt={{ base: 2, md: 0 }}
                    width={{ base: '100%', md: 'auto' }}
                    spacing={1}
                  >
                    <IconButton
                      aria-label="Decrease quantity"
                      icon={<MinusIcon size={16} />}
                      onClick={() => handleDecrement(item.id, item.quantity)}
                      size="sm"
                      variant="outline"
                      colorScheme="gray"
                      isDisabled={item.quantity <= 1}
                    />
                    <Input
                      value={item.quantity}
                      onChange={(e) => {
                        const value = parseInt(e.target.value);
                        if (!isNaN(value) && value > 0) {
                          updateQuantity(item.id, value);
                        }
                      }}
                      type="number"
                      min={1}
                      max={99}
                      w="50px"
                      textAlign="center"
                      size="sm"
                    />
                    <IconButton
                      aria-label="Increase quantity"
                      icon={<PlusIcon size={16} />}
                      onClick={() => handleIncrement(item.id, item.quantity)}
                      size="sm"
                      variant="outline"
                      colorScheme="gray"
                    />
                  </HStack>
                  
                  {/* Total */}
                  <Box 
                    flex="1" 
                    textAlign={{ base: 'right', md: 'center' }}
                    fontWeight="semibold" 
                    mt={{ base: 2, md: 0 }}
                  >
                    ${(item.price * item.quantity).toFixed(2)}
                  </Box>
                  
                  {/* Remove */}
                  <Box ml={4} mt={{ base: 2, md: 0 }}>
                    <IconButton
                      aria-label="Remove item"
                      icon={<TrashIcon size={18} />}
                      variant="ghost"
                      colorScheme="red"
                      size="sm"
                      onClick={() => handleRemove(item.id, item.name)}
                    />
                  </Box>
                </Flex>
              ))}
            </VStack>
          </Box>
          
          <Flex justify="space-between" mt={6} flexWrap="wrap">
            <Button 
              as={RouterLink} 
              to="/products"
              leftIcon={<ChevronRightIcon size={18} />}
              variant="outline"
            >
              Continue Shopping
            </Button>
          </Flex>
        </GridItem>
        
        {/* Order Summary */}
        <GridItem>
          <Box 
            bg="white" 
            borderRadius="md"
            boxShadow="sm"
            p={6}
          >
            <Heading size="md" mb={4}>Order Summary</Heading>
            
            <VStack spacing={4} align="stretch">
              <Flex justify="space-between">
                <Text>Subtotal</Text>
                <Text fontWeight="semibold">${totalPrice.toFixed(2)}</Text>
              </Flex>
              
              <Flex justify="space-between">
                <Text>Shipping</Text>
                <Text fontWeight="semibold">Free</Text>
              </Flex>
              
              <Box>
                <FormControl>
                  <Flex>
                    <Input
                      placeholder="Coupon Code"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value)}
                      mr={2}
                    />
                    <Button onClick={handleApplyCoupon}>Apply</Button>
                  </Flex>
                </FormControl>
              </Box>
              
              <Divider />
              
              <Flex justify="space-between" fontWeight="bold" fontSize="lg">
                <Text>Total</Text>
                <Text color="brand.500">${totalPrice.toFixed(2)}</Text>
              </Flex>
              
              <Button 
                colorScheme="brand"
                size="lg"
                w="full"
                mt={2}
                as={RouterLink}
                to="/checkout"
              >
                Checkout
              </Button>
            </VStack>
          </Box>
        </GridItem>
      </Grid>
    </Container>
  );
};

export default CartPage;

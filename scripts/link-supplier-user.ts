import { PrismaClient } from '@prisma/client';

process.env.DATABASE_URL = "mongodb://localhost:27017/stockly";
const prisma = new PrismaClient();

async function main() {
  console.log("Linking test@supplier.com to a mock Supplier entity...");
  const supplierUser = await prisma.user.findUnique({ where: { email: 'test@supplier.com' } });
  
  if (!supplierUser) {
    console.log("No supplier user found.");
    return;
  }

  // Ensure Demo Supplier belongs to test@supplier.com
  const supplier = await prisma.supplier.findFirst({
    where: { name: { startsWith: 'Demo Supplier' } }
  });

  if (supplier) {
    await prisma.supplier.update({
      where: { id: supplier.id },
      data: { userId: supplierUser.id }
    });
    console.log(`Successfully linked "${supplier.name}" to test@supplier.com`);

    // Let's also link "Supplier one" so they have even more data! Wait, `findFirst` is used in the codebase so they can only have ONE supplier.
    // That's fine.
  } else {
    // Fallback to any supplier
    const anySupplier = await prisma.supplier.findFirst();
    if (anySupplier) {
       await prisma.supplier.update({
         where: { id: anySupplier.id },
         data: { userId: supplierUser.id }
       });
       console.log(`Successfully linked "${anySupplier.name}" to test@supplier.com`);
    } else {
       console.log("No suppliers exist in db.");
    }
  }
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());

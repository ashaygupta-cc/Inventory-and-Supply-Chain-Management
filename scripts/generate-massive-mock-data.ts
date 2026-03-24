import { PrismaClient } from '@prisma/client';

process.env.DATABASE_URL = "mongodb://localhost:27017/stockly";

const prisma = new PrismaClient();

function randomDate(start: Date, end: Date) {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

function randomElement<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

async function main() {
  console.log('Generating massive mock data for dashboard panels...');

  // Ensure demo accounts exist to own the data
  let admin = await prisma.user.findUnique({ where: { email: 'test@admin.com' } });
  if (!admin) {
    admin = await prisma.user.findFirst({ where: { role: 'admin' } });
  }
  let client = await prisma.user.findUnique({ where: { email: 'test@client.com' } });
  let supplierUser = await prisma.user.findUnique({ where: { email: 'test@supplier.com' } });

  if (!admin) throw new Error("No admin user found to own records.");
  const ownerId = admin.id;
  const clientId = client ? client.id : admin.id;

  const nonce = Date.now().toString().slice(-6);

  // 1. Create Suppliers
  const supplierNames = ['Supplier one', 'Demo Supplier', 'Techtronics Global', 'Audio Masters', 'VisionTech'];
  const suppliers = [];
  for (const name of supplierNames) {
    suppliers.push(
      await prisma.supplier.create({
        data: {
          name: `${name} ${nonce}`,
          userId: ownerId,
          createdBy: ownerId,
          status: true,
          description: `Leading supplier for ${name}`
        }
      })
    );
  }
  console.log(`Created ${suppliers.length} Suppliers`);

  // 2. Create Categories
  const categoryNames = ['Phone', 'Tablet', 'Television', 'Music Instruments', 'Headphone', 'Laptop'];
  const categories = [];
  for (const name of categoryNames) {
    categories.push(
      await prisma.category.create({
        data: {
          name: `${name} ${nonce}`,
          userId: ownerId,
          createdBy: ownerId,
          status: true,
          description: `${name} category items`
        }
      })
    );
  }
  console.log(`Created ${categories.length} Categories`);

  // 3. Create Warehouses
  const warehouseNames = ['Main Storage Alpha', 'West Coast Dist', 'East Coast Hub'];
  const warehouses = [];
  for (const name of warehouseNames) {
    warehouses.push(
      await prisma.warehouse.create({
        data: {
          name: `${name} ${nonce}`,
          userId: ownerId,
          createdBy: ownerId,
          type: 'main',
          status: true
        }
      })
    );
  }
  console.log(`Created ${warehouses.length} Warehouses`);

  // 4. Create Products from Screenshots + Extras
  const productTemplates = [
    { name: 'samsung sm12', skuPrefix: 'sam', price: 100.00, cat: 'Phone', sup: 'Supplier one' },
    { name: 'tab5 samsung', skuPrefix: 'sane', price: 200.00, cat: 'Tablet', sup: 'Supplier one' },
    { name: 'DELL', skuPrefix: 'TR', price: 2600.00, cat: 'Television', sup: 'Demo Supplier' },
    { name: 'Drums', skuPrefix: 'DM', price: 99.00, cat: 'Music Instruments', sup: 'Demo Supplier' },
    { name: 'Beats', skuPrefix: 'HP', price: 70.00, cat: 'Headphone', sup: 'Demo Supplier' },
    { name: 'iPhone', skuPrefix: 'MP', price: 80.00, cat: 'Phone', sup: 'Supplier one' },
    { name: 'Telephone', skuPrefix: 'TL', price: 50.00, cat: 'Phone', sup: 'Demo Supplier' },
    { name: 'Sony TV', skuPrefix: 'ST', price: 450.00, cat: 'Television', sup: 'Demo Supplier' },
    { name: 'MacBook Pro', skuPrefix: 'MBP', price: 1999.00, cat: 'Laptop', sup: 'Techtronics Global' },
    { name: 'Electric Guitar', skuPrefix: 'EG', price: 350.00, cat: 'Music Instruments', sup: 'Audio Masters' },
    { name: 'AirPods Max', skuPrefix: 'APM', price: 549.00, cat: 'Headphone', sup: 'Audio Masters' },
    { name: 'LG OLED 65', skuPrefix: 'LGO', price: 1200.00, cat: 'Television', sup: 'VisionTech' },
    { name: 'Galaxy S24', skuPrefix: 'GS', price: 899.00, cat: 'Phone', sup: 'Supplier one' },
    { name: 'iPad Air', skuPrefix: 'IPA', price: 599.00, cat: 'Tablet', sup: 'Techtronics Global' },
    { name: 'Yamaha Keyboard', skuPrefix: 'YK', price: 850.00, cat: 'Music Instruments', sup: 'Audio Masters' },
    { name: 'Bose QuietComfort', skuPrefix: 'BQC', price: 299.00, cat: 'Headphone', sup: 'Audio Masters' },
    { name: 'Dell XPS 15', skuPrefix: 'XPS', price: 1500.00, cat: 'Laptop', sup: 'Techtronics Global' },
    { name: 'Pixel 8 Pro', skuPrefix: 'P8P', price: 999.00, cat: 'Phone', sup: 'Supplier one' }
  ];

  const products = [];
  for (let i = 0; i < productTemplates.length; i++) {
    const t = productTemplates[i];
    
    // Find matched category/supplier
    const cat = categories.find(c => c.name.startsWith(t.cat)) || categories[0];
    const sup = suppliers.find(s => s.name.startsWith(t.sup)) || suppliers[0];

    // Some products 0 stock, some low, some high
    let qty = Math.floor(Math.random() * 80) + 10;
    let status = 'Available';
    if (t.name === 'DELL') {
      qty = 0;
      status = 'Stock Out';
    } else if (i % 5 === 0) {
      qty = Math.floor(Math.random() * 15) + 1;
      status = 'Stock Low';
    }

    const prodDate = new Date();
    prodDate.setDate(prodDate.getDate() - Math.floor(Math.random() * 30));

    const p = await prisma.product.create({
      data: {
        name: t.name,
        sku: `${t.skuPrefix}${Math.floor(100 + Math.random() * 900)}-${nonce}`,
        price: t.price,
        quantity: BigInt(qty),
        status: status,
        categoryId: cat.id,
        supplierId: sup.id,
        userId: ownerId,
        createdBy: ownerId,
        createdAt: prodDate,
        expirationDate: Math.random() > 0.5 ? new Date(Date.now() + 1000 * 60 * 60 * 24 * 365 * (1 + Math.random() * 5)) : null
      }
    });
    products.push({ ...p, NumberQty: qty });

    // Allocate stock to random warehouses
    if (qty > 0) {
      let remaining = qty;
      for (const w of warehouses) {
        if (remaining <= 0) break;
        const alloc = Math.floor(Math.random() * remaining) + 1;
        await prisma.stockAllocation.create({
          data: {
            productId: p.id,
            warehouseId: w.id,
            quantity: BigInt(alloc),
            userId: ownerId
          }
        });
        remaining -= alloc;
      }
      // Put rest in main
      if (remaining > 0) {
        await prisma.stockAllocation.create({
          data: {
            productId: p.id,
            warehouseId: warehouses[0].id,
            quantity: BigInt(remaining),
            userId: ownerId
          }
        }).catch(()=>null); // Ignore unique constraint if hit
      }
    }
  }
  console.log(`Created ${products.length} Products and Stock Allocations`);

  // 5. Generate 25 Orders to populate Revenue/Profit/Status charts
  const statuses = ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled', 'Delivered', 'Delivered', 'Shipped'];
  const paymentStatuses = ['unpaid', 'paid', 'refunded', 'partial', 'paid', 'paid'];
  
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 40); // Orders over last 40 days

  let orderCount = 0;
  for (let i = 1; i <= 25; i++) {
    const orderDate = randomDate(start, end);
    const numItems = Math.floor(Math.random() * 4) + 1;
    
    // Pick random products
    const orderItemsData = [];
    let subtotal = 0;
    
    for (let j = 0; j < numItems; j++) {
      const p = randomElement(products);
      const q = Math.floor(Math.random() * 3) + 1;
      const lineTotal = p.price * q;
      subtotal += lineTotal;
      orderItemsData.push({
        productId: p.id,
        productName: p.name,
        sku: p.sku,
        quantity: q,
        price: p.price,
        subtotal: lineTotal
      });
    }

    const tStatus = randomElement(statuses);
    const pStatus = tStatus === 'Cancelled' ? 'refunded' : (tStatus === 'Pending' ? 'unpaid' : randomElement(paymentStatuses));

    const ord = await prisma.order.create({
      data: {
        orderNumber: `ORD-${orderDate.getFullYear()}-${(orderDate.getMonth()+1).toString().padStart(2,'0')}${orderDate.getDate().toString().padStart(2,'0')}-${orderDate.getHours()}${orderDate.getMinutes()}-${i.toString().padStart(4,'0')}-${nonce}`,
        userId: ownerId,
        clientId: Math.random() > 0.5 ? clientId : null,
        status: tStatus,
        paymentStatus: pStatus,
        subtotal: subtotal,
        total: subtotal + (subtotal * 0.05), // add 5% tax
        createdAt: orderDate,
        createdBy: ownerId
      }
    });

    // Create order items sequentially to avoid nested writes transaction!
    for (const item of orderItemsData) {
      await prisma.orderItem.create({
        data: {
          orderId: ord.id,
          ...item
        }
      });
    }

    // Create Invoice for non-cancelled orders that are paid or pending
    if (tStatus !== 'Cancelled') {
      await prisma.invoice.create({
        data: {
          invoiceNumber: `INV-${orderDate.getFullYear()}-${i.toString().padStart(4,'0')}-${nonce}`,
          orderId: ord.id,
          userId: ownerId,
          clientId: Math.random() > 0.5 ? clientId : null,
          status: pStatus === 'paid' ? 'paid' : 'draft',
          subtotal: ord.subtotal,
          total: ord.total,
          amountPaid: pStatus === 'paid' ? ord.total : 0,
          dueDate: new Date(orderDate.getTime() + 1000 * 60 * 60 * 24 * 14),
          createdAt: orderDate,
          createdBy: ownerId
        }
      });
    }
    
    orderCount++;
  }
  console.log(`Created ${orderCount} Orders with Items and Invoices`);

  console.log('Massive mock data generation completed! All panels should now be populated beautifully.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

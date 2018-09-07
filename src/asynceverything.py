import asyncio


test1runs = 0
async def test1():
    global test1runs
    test1runs += 1
    print(f"Inni test1, kjøring {test1runs}")
    await test2()
    print(f"Inni test1SLUTT, kjøring {test1runs}")


test2runs = 0
async def test2():
    global test2runs
    test2runs += 1
    print(f"Inni test2, kjøring nr {test2runs}")
    await asyncio.sleep(1)
    print(f"Inni test2SLUTT, kjøring nr {test2runs}")


async def test3():
    #await asyncio.sleep(0.3)
    print("Waddlin' here")
    await asyncio.sleep(0.3)
    print("Waddlin' here")
    await asyncio.sleep(0.3)
    print("Waddlin' here")


async def test4():
    print("Test 4 started")
    await asyncio.sleep(0.5)
    print("Test 4 finished")


async def test5():
    await asyncio.sleep(0.1)
    print("Test 5 started")
    await asyncio.sleep(0.3)
    print("Test 5 finished")


def main():
    asyncio.ensure_future(test1())
    asyncio.ensure_future(test3())
    asyncio.get_event_loop().run_forever()


def main2():
    asyncio.gather(test4(), test5())
    asyncio.get_event_loop().run_forever()
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(test4())
    #loop.run_until_complete(test5())


if __name__ == "__main__":
    main2()

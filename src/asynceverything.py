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
    await asyncio.sleep(0.3)
    print("Waddlin' here")
    await asyncio.sleep(0.3)
    print("Waddlin' here")
    await asyncio.sleep(0.3)
    print("Waddlin' here")


def main():
    asyncio.ensure_future(test1())
    asyncio.ensure_future(test3())
    asyncio.get_event_loop().run_until_complete()


if __name__ == "__main__":
    main()

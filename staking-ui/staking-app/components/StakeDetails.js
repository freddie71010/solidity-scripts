import { useMoralis, useWeb3Contract } from "react-moralis"
import { stakingAddress, rewardTokenAddress, stakingABI, rewardTokenABI } from "../constants/index"
import { useEffect, useState } from "react"
import { ethers } from "ethers"


export default function StakeDetails() {
    const { account, isWeb3Enabled } = useMoralis()
    const [rtBalance, setRtBalance] = useState("0")
    const [stakedBalance, setStakedBalance] = useState("0")
    const [earnedBalance, setEarnedBalance] = useState("0")


    const { runContractFunction: getStakedBalance } = useWeb3Contract({
        abi: stakingABI,
        contractAddress: stakingAddress,
        functionName: "getStaked",
        params: {
            account: account,
        }
    })

    const { runContractFunction: getEarnedBalance } = useWeb3Contract({
        abi: stakingABI,
        contractAddress: stakingAddress,
        functionName: "earned",
        params: {
            account: account,
        }
    })


    const { runContractFunction: getRtBalance } = useWeb3Contract({
        abi: rewardTokenABI,
        contractAddress: rewardTokenAddress,
        functionName: "balanceOf",
        params: {
            account: account,
        }
    })


    async function updateUiValues() {
        const earnedBalanceFromContract = (await getEarnedBalance({ onError: (error) => console.log(error) })
        ).toString()
        const formattedEarnedBalanceFromContract = ethers.utils.formatUnits(earnedBalanceFromContract, "ether")
        setEarnedBalance(formattedEarnedBalanceFromContract)

        const stakedBalanceFromContract = (await getStakedBalance({ onError: (error) => console.log(error) })
        ).toString()
        const formattedStakedBalanceFromContract = ethers.utils.formatUnits(stakedBalanceFromContract, "ether")
        setStakedBalance(formattedStakedBalanceFromContract)

        const rtBalanceFromContract = (await getRtBalance({ onError: (error) => console.log(error) })
        ).toString()
        const formattedRtBalanceFromContract = ethers.utils.formatUnits(rtBalanceFromContract, "ether")
        setRtBalance(formattedRtBalanceFromContract)
    }

    useEffect((() => {
        // update UI and get balances
        if (isWeb3Enabled && account) {
            updateUiValues()
        }
    }), [account, isWeb3Enabled])

    return (
        <div>
            <h1 className="py-4 px-4 font-bold text-center text-3xl">Summary</h1>
            <div>RT balance is: {rtBalance}</div>
            <div>Staked balance is: {stakedBalance}</div>
            <div>Earned balance is: {earnedBalance}</div>
        </div>
    )
}

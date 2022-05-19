// staking abi
// staking address
// how much they want to stake
// approve reward token

import { useMoralis, useWeb3Contract } from "react-moralis"
import { stakingAddress, rewardTokenAddress, stakingABI, rewardTokenABI } from "../constants/index"
import { Form } from "web3uikit"
import { ethers } from "ethers"


export default function StakeForm() {
    const { runContractFunction } = useWeb3Contract()

    let approveOptions = {
        abi: rewardTokenABI,
        contractAddress: rewardTokenAddress,
        functionName: "approve",
    }
    let stakeOptions = {
        abi: stakingABI,
        contractAddress: stakingAddress,
        functionName: "stake",
    }
    let withdrawOptions = {
        abi: stakingABI,
        contractAddress: stakingAddress,
        functionName: "withdraw",
    }

    async function handleStakeSubmit(data) {
        const amountToApprove = data.data[0].inputResult
        approveOptions.params = {
            amount: ethers.utils.parseUnits(amountToApprove, "ether").toString(),
            spender: stakingAddress,
        }
        console.log("Approving stake...")
        const tx = await runContractFunction({
            params: approveOptions,
            onError: (error) => console.log(error),
            onSuccess: () => {
                handleApproveSuccess(approveOptions.params.amount)
            },
        })
    }

    async function handleApproveSuccess(amountToStakeFormatted) {
        stakeOptions.params = {
            amount: amountToStakeFormatted
        }
        console.log(`Staking ${stakeOptions.params.amount} RT Token`)
        const tx = await runContractFunction({
            params: stakeOptions,
            onError: (error) => console.log(error),
        })
        await tx.wait(1)
        console.log("Tx has been confirmed by 1 block")
    }


    async function handleWithdrawSubmit(data) {
        const amountToApprove = data.data[0].inputResult
        approveOptions.params = {
            amount: ethers.utils.parseUnits(amountToApprove, "ether").toString(),
            spender: stakingAddress,
        }
        console.log("Approving withdraw...")
        const tx = await runContractFunction({
            params: approveOptions,
            onError: (error) => console.log(error),
            onSuccess: () => {
                handleWithdrawApproveSuccess(approveOptions.params.amount)
            },
        })
    }

    async function handleWithdrawApproveSuccess(amountToWithdrawFormatted) {
        withdrawOptions.params = {
            amount: amountToWithdrawFormatted
        }
        console.log(`Withdrawing ${withdrawOptions.params.amount} RT Tokens`)
        const tx = await runContractFunction({
            params: withdrawOptions,
            onError: (error) => console.log(error),
        })
        await tx.wait(1)
        console.log("Tx has been confirmed by 1 block")
    }

    return (
        <div>
            <div>
                <Form
                    onSubmit={handleStakeSubmit}
                    data={[{
                        inputWidth: "50%",
                        name: "Amount to stake in ETH",
                        type: "number",
                        value: "",
                        key: "amount"

                    }]}
                ></Form>
            </div><div>
                <Form
                    onSubmit={handleWithdrawSubmit}
                    data={[{
                        inputWidth: "50%",
                        name: "Amount to withdraw in ETH",
                        type: "number",
                        value: "",
                        key: "amount"

                    }]}
                ></Form>
            </div>
        </div>


    )

}

import { getInput, setFailed, setOutput } from '@actions/core';
import { getOctokit, context } from '@actions/github';
import { Endpoints } from '@octokit/types';

const getUserInputs = () => {
    const sendTime = getInput("sendTime") || "19:00"
    return {
      sendTime
    };
  };

async function main() {
    
}

try {
    main()
} catch (error) {
    setFailed(`${(error as unknown as { message: string }).message} -> ${error}`);
}
package hotdog.BFCMiner;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.collections4.IterableUtils;
import org.checkerframework.checker.units.qual.A;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.api.errors.TransportException;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.revwalk.RevCommit;


public class CommitMiner {

    private List<RevCommit> commitList;
    private File file = null;
    private Git git;
    private boolean completed = false;
    //	private String filePath = "/data/CGYW/clones/";
	private String filePath = "/Users/nayeawon/Desktop/Exp/";
//	private String filePath = "/Users/leechanggong/Desktop/Exp/";
//    private String filePath = "/home/leechanggong/research/";
    //	private String filePath = "/Users/leechanggong/Desktop/";
    private String matcherGroup;

    public CommitMiner(String path) {
        Pattern pattern = Pattern.compile("(git@|ssh|https://)github.com/()(.*?)$");
        Matcher matcher = pattern.matcher(path);

        if (matcher.find()) {
            matcherGroup = matcher.group(3);
            file = new File(filePath  +  matcherGroup + "/.git");
            filePath = filePath + matcherGroup;
            if (file.exists()) {
                try {
                    git = Git.open(file);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                try {
                    git = Git.cloneRepository()
                            .setURI(path)
                            .setDirectory(file).call();
                } catch (GitAPIException e) {
                    System.out.println("\nno CredentialsProvider(Authentication Problem)\n");
                    return;
                }
            }
        } else {
            try {
                git = Git.open(new File(path + "/.git"));
            } catch (IOException e) {
                e.printStackTrace();
            }
            matcherGroup = path.substring(filePath.length());
            filePath = filePath + matcherGroup;
        }
        try {
            Iterable<RevCommit> walk = git.log().all().call();
            commitList = IterableUtils.toList(walk);
            completed = true;
        } catch (Exception e) { System.out.println("Exception occurred, Skip to next project\n"); }
        return;
    }

    public List<RevCommit> getCommitList() {
        return commitList;
    }

    public RevCommit getCommit(String path, String commitID) {
        try {
            file = new File(filePath + path + "/.git");
            if (file.exists())
                git = Git.open(file);
            else {
                try {
                    git = Git.cloneRepository()
                            .setURI("https://github.com/" + path)
                            .setDirectory(file).call();
                } catch (TransportException e) {
                    System.out.println("\nno CredentialsProvider(Authentication Problem)\n");
                    return null;
                }
            }
            git = Git.open(new File(filePath + path + "/.git"));
            Iterable<RevCommit> walk = git.log().all().call();
            commitList = IterableUtils.toList(walk);
            for (RevCommit commit : commitList) {
                if (commit.getName().equals(commitID)) return commit;
            }
        } catch (Exception e) {
            e.printStackTrace();
        } return null;
    }
    public ArrayList<String> extractID () {
        ArrayList<String> idList = new ArrayList<>();
        for (RevCommit temp : commitList) {
            //System.out.println(temp);
            idList.add(temp.getName());
        }
        return idList;
    }

    public Repository getRepo() {
        return git.getRepository();
    }

    public boolean isCompleted() { return completed; }

    public String getFilePath() { return filePath; }

    public String getMatcherGroup() { return matcherGroup; }

}



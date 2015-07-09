package org.jboss.da.listings.impl.service;

import java.util.List;

import org.jboss.da.listings.api.dao.ArtifactDAO;
import org.jboss.da.listings.api.model.Artifact;
import org.jboss.da.listings.api.service.ArtifactService;

/**
 * 
 * @author Jozef Mrazek <jmrazek@redhat.com>
 *
 */
public abstract class ArtifactServiceImpl<T extends Artifact> implements ArtifactService<T> {

    private Class type;

    public ArtifactServiceImpl(Class<T> type) {
        this.type = type;
    }

    protected abstract ArtifactDAO<T> getDAO();

    @Override
    public boolean addArtifact(String groupId, String artifactId, String version) {
        if (getDAO().findArtifact(groupId, artifactId, version) != null) {
            return false;
        }
        try {
            T artifact = (T) type.newInstance();
            artifact.setArtifactId(artifactId);
            artifact.setGroupId(groupId);
            artifact.setVersion(version);
            getDAO().create(artifact);
            return true;
        } catch (InstantiationException | IllegalAccessException e) {
            e.printStackTrace();
        }
        return false;
    }

    @Override
    public T getArtifact(String groupId, String artifactId, String version) {
        return getDAO().findArtifact(groupId, artifactId, version);
    }

    @Override
    public boolean isArtifactPresent(String groupId, String artifactId, String version) {
        return (getDAO().findArtifact(groupId, artifactId, version) != null);
    }

    @Override
    public List<T> getAll() {
        return getDAO().findAll();
    }
}
